from pymongo import MongoClient
from bson import ObjectId
import requests
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

client = MongoClient(os.environ["MONGODB_CONN"])
db = client.ff_db
matchups = db["Matchups"]
leagues = db["Leagues"]
contestants = db["Contestants"]


def generate_schedule():
    unscheduled_leagues = leagues.find({"scheduled": False, "full": True})
    for league in unscheduled_leagues:
        teams = league["size"]
        weeks = league["regular_season_weeks"]

        round_robin_cycle_length = teams - 1
        number_of_cycles = (weeks // round_robin_cycle_length) + 1
        matches = []
        half_size = teams // 2

        contestant_ids = []
        contestant_names = []
        league_contestants = contestants.find({"league_id": league["_id"]})
        for con in league_contestants:
            contestant_ids.append(con["_id"])
            contestant_names.append(con["team_name"])

        team_list = list(range(teams))
        week = 1

        for cycle in range(number_of_cycles):
            for round in range(round_robin_cycle_length):
                round_matches = []
                for i in range(half_size):
                    doc = {}
                    doc["league_id"] = league["_id"]
                    doc["week"] = week
                    doc["team_1_id"] = contestant_ids[i]
                    doc["team_1_name"] = contestant_names[i]
                    doc["team_1_score"] = 0
                    doc["team_2_id"] = contestant_ids[-i-1]
                    doc["team_2_name"] = contestant_names[-i-1]
                    doc["team_2_score"] = 0
                    doc["started"] = False
                    doc["finished"] = False
                    matchups.insert_one(doc)
                contestant_ids.insert(1, contestant_ids.pop())
                contestant_names.insert(1, contestant_names.pop())

                week = week + 1
                if week > weeks:
                    break
                
        # # update league schedule bool
        leagues.update_one(
            {"_id": ObjectId(league["_id"])},
            {"$set": {
                "scheduled": True
            }}
        )  

        return "schedule generated"

generate_schedule()