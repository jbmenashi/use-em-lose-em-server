from pymongo import MongoClient
from bson import ObjectId
import requests
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

client = MongoClient(os.environ["MONGODB_CONN"])
db = client.ff_db
player_projections = db["PlayerProjections"]

projection_season = 2023
projection_week = 1



def get_player_projections():
    projection_inserts = []

    res = requests.get(f"https://api.sportsdata.io/v3/nfl/projections/json/PlayerGameProjectionStatsByWeek/{projection_season}/{projection_week}?key=10fd23b6dc3d47f486e1159d2bf02e2b")

    for player in res.json():
        score = (player["PassingYards"] * 0.04) + (player["PassingTouchdowns"] * 4) + (player["PassingInterceptions"] * -1) + (player["RushingYards"] * 0.1) + (player["Receptions"] * 0.5) + (player["ReceivingYards"] * 0.1) + (player["Fumbles"] * -2) + (player["Touchdowns"] * 6)

        if projection_exists := player_projections.find_one({
                "player_id": player["PlayerID"],
                "season": projection_season,
                "week": projection_week
            }) is not None:
            found_projection = player_projections.find_one({
                "player_id": player["PlayerID"],
                "season": projection_season,
                "week": projection_week
            })
            update = 0
            if found_projection["pass_yds"] != player["PassingYards"]:
                update = 1
            if found_projection["pass_tds"] != player["PassingTouchdowns"]:
                update = 1
            if found_projection["ints"] != player["PassingInterceptions"]:
                update = 1    
            if found_projection["rush_yds"] != player["RushingYards"]:
                update = 1     
            if found_projection["receptions"] != player["Receptions"]:
                update = 1    
            if found_projection["rec_yds"] != player["ReceivingYards"]:
                update = 1    
            if found_projection["fumbles"] != player["Fumbles"]:
                update = 1    
            if found_projection["tds"] != player["Touchdowns"]:
                update = 1    

            if update == 1:
                player_projections.update_one(
                    {"_id": ObjectId(found_projection["_id"])},
                    {"$set": {
                        "pass_yds": player["PassingYards"],
                        "pass_tds": player["PassingTouchdowns"],
                        "ints": player["PassingInterceptions"],
                        "rush_yds": player["RushingYards"],
                        "receptions": player["Receptions"],
                        "rec_yds": player["ReceivingYards"],
                        "fumbles": player["Fumbles"],
                        "tds": player["Touchdowns"],
                        "score": score
                    }}
                )       
                print(f"updated projection for {player["Name"]} for week {projection_week}")
            else:
                print(f"no projection change for {player["Name"]} for week {projection_week}")
                    
        else:
            if player["Position"] in ["QB", "RB", "WR", "TE"]:
                projection = {}
                projection["player_id"] = player["PlayerID"]
                projection["player_name"] = player["Name"]
                projection["team_id"] = player["TeamID"]
                projection["team_abbv"] = player["Team"]
                projection["season"] = projection_season
                projection["week"] = projection_week
                projection["opponent"] = player["Opponent"]
                projection["opponent_team_id"] = player["OpponentID"]
                projection["location"] = player["HomeOrAway"]
                projection["pass_yds"] = player["PassingYards"]
                projection["pass_tds"] = player["PassingTouchdowns"]
                projection["ints"] = player["PassingInterceptions"]
                projection["rush_yds"] = player["RushingYards"]
                projection["receptions"] = player["Receptions"]
                projection["rec_yds"] = player["ReceivingYards"]
                projection["fumbles"] = player["Fumbles"]
                projection["tds"] = player["Touchdowns"]
                projection["two_pt_conv"] = 0
                projection["def_pts_allowed"] = 0
                projection["def_sacks"] = 0
                projection["def_fumble_rec"] = 0
                projection["def_ints"] = 0
                projection["def_blk_kicks"] = 0
                projection["def_safeties"] = 0
                projection["def_tds_scored"] = 0
                projection["score"] = score
                projection_inserts.append(projection)
                
                print(f"inserted new projection for {player["Name"]} for week {projection_week}")

    res = requests.get(f"https://api.sportsdata.io/v3/nfl/projections/json/FantasyDefenseProjectionsByGame/{projection_season}/{projection_week}?key=10fd23b6dc3d47f486e1159d2bf02e2b")

    for player in res.json():
        score = (player["Sacks"]) + (player["FumblesRecovered"] * 2) + (player["Interceptions"] * 2) + (player["BlockedKicks"] * 2) + (player["Safeties"] * 3) + (player["TouchdownsScored"] * 6)       

        if player["PointsAllowed"] == 0:
            score += 10
        elif player["PointsAllowed"] > 0 and player["PointsAllowed"] < 7:
            score += 7
        elif player["PointsAllowed"] >= 7 and player["PointsAllowed"] < 14:
            score += 4
        elif player["PointsAllowed"] >= 14 and player["PointsAllowed"] < 21:
            score += 1
        elif player["PointsAllowed"] >= 21 and player["PointsAllowed"] < 28:
            score += 0
        elif player["PointsAllowed"] >= 28 and player["PointsAllowed"] < 35:
            score += -1
        else:
            score += -4

        if projection_exists := player_projections.find_one({
                "player_id": player["PlayerID"],
                "season": projection_season,
                "week": projection_week
            }) is not None:
            found_projection = player_projections.find_one({
                "player_id": player["PlayerID"],
                "season": projection_season,
                "week": projection_week
            })
            update = 0
            if found_projection["def_pts_allowed"] != player["PointsAllowed"]:
                update = 1
            if found_projection["def_sacks"] != player["Sacks"]:
                update = 1
            if found_projection["def_fumble_rec"] != player["FumblesRecovered"]:
                update = 1    
            if found_projection["def_ints"] != player["Interceptions"]:
                update = 1     
            if found_projection["def_blk_kicks"] != player["BlockedKicks"]:
                update = 1    
            if found_projection["def_safeties"] != player["Safeties"]:
                update = 1    
            if found_projection["def_tds_scored"] != player["TouchdownsScored"]:
                update = 1      

            if update == 1:
                player_projections.update_one(
                    {"_id": ObjectId(found_projection["_id"])},
                    {"$set": {
                        "def_pts_allowed": player["PointsAllowed"],
                        "def_sacks": player["Sacks"],
                        "def_fumble_rec": player["FumblesRecovered"],
                        "def_ints": player["Interceptions"],
                        "def_blk_kicks": player["BlockedKicks"],
                        "def_safeties": player["Safeties"],
                        "def_tds_scored": player["TouchdownsScored"],
                        "score": score
                    }}
                )       
                print(f"updated projection for {player["Name"]} for week {projection_week}")
            else:
                print(f"no projection change for {player["Name"]} for week {projection_week}")
                    
        else:
            projection = {}
            projection["player_id"] = player["TeamID"]
            projection["player_name"] = player["Team"] + " Defense"
            projection["team_id"] = player["TeamID"]
            projection["team_abbv"] = player["Team"]
            projection["season"] = projection_season
            projection["week"] = projection_week
            projection["opponent"] = player["Opponent"]
            projection["opponent_team_id"] = player["OpponentID"]
            projection["location"] = player["HomeOrAway"]
            projection["pass_yds"] = 0
            projection["pass_tds"] = 0
            projection["ints"] = 0
            projection["rush_yds"] = 0
            projection["receptions"] = 0
            projection["rec_yds"] = 0
            projection["fumbles"] = 0
            projection["tds"] = 0
            projection["two_pt_conv"] = 0
            projection["def_pts_allowed"] = player["PointsAllowed"]
            projection["def_sacks"] = player["Sacks"]
            projection["def_fumble_rec"] = player["FumblesRecovered"]
            projection["def_ints"] = player["Interceptions"]
            projection["def_blk_kicks"] = player["BlockedKicks"]
            projection["def_safeties"] = player["Safeties"]
            projection["def_tds_scored"] = player["TouchdownsScored"]
            projection["score"] = score
            projection_inserts.append(projection)
            
            print(f"inserted new projection for {player["Team"]} for week {projection_week}")

    if len(projection_inserts) > 0:
        player_projections.insert_many(projection_inserts)

    return

get_player_projections()