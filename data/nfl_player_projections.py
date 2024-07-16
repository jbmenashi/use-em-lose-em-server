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

projection_season = 2024
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
            if found_projection["stats"]["pass_yds"] != player["PassingYards"]:
                update = 1
            if found_projection["stats"]["pass_tds"] != player["PassingTouchdowns"]:
                update = 1
            if found_projection["stats"]["ints"] != player["PassingInterceptions"]:
                update = 1    
            if found_projection["stats"]["rush_yds"] != player["RushingYards"]:
                update = 1     
            if found_projection["stats"]["receptions"] != player["Receptions"]:
                update = 1    
            if found_projection["stats"]["rec_yds"] != player["ReceivingYards"]:
                update = 1    
            if found_projection["stats"]["fumbles"] != player["Fumbles"]:
                update = 1    
            if found_projection["stats"]["tds"] != player["Touchdowns"]:
                update = 1    

            if update == 1:
                player_projections.update_one(
                    {"_id": ObjectId(found_projection["_id"])},
                    {"$set": {
                        "stats.pass_yds": player["PassingYards"],
                        "stats.pass_tds": player["PassingTouchdowns"],
                        "stats.ints": player["PassingInterceptions"],
                        "stats.rush_yds": player["RushingYards"],
                        "stats.receptions": player["Receptions"],
                        "stats.rec_yds": player["ReceivingYards"],
                        "stats.fumbles": player["Fumbles"],
                        "stats.tds": player["Touchdowns"],
                        "stats.score": score
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
                projection["sport"] = "NFL"
                projection["season"] = projection_season
                projection["week"] = projection_week
                projection["opponent"] = player["Opponent"]
                projection["opponent_team_id"] = player["OpponentID"]
                projection["location"] = player["HomeOrAway"]
                projection["stats"] = {}
                projection["stats"]["pass_yds"] = player["PassingYards"]
                projection["stats"]["pass_tds"] = player["PassingTouchdowns"]
                projection["stats"]["ints"] = player["PassingInterceptions"]
                projection["stats"]["rush_yds"] = player["RushingYards"]
                projection["stats"]["receptions"] = player["Receptions"]
                projection["stats"]["rec_yds"] = player["ReceivingYards"]
                projection["stats"]["fumbles"] = player["Fumbles"]
                projection["stats"]["tds"] = player["Touchdowns"]
                projection["stats"]["two_pt_conv"] = 0
                projection["stats"]["def_pts_allowed"] = 0
                projection["stats"]["def_sacks"] = 0
                projection["stats"]["def_fumble_rec"] = 0
                projection["stats"]["def_ints"] = 0
                projection["stats"]["def_blk_kicks"] = 0
                projection["stats"]["def_safeties"] = 0
                projection["stats"]["def_tds_scored"] = 0
                projection["stats"]["score"] = score
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
            if found_projection["stats"]["def_pts_allowed"] != player["PointsAllowed"]:
                update = 1
            if found_projection["stats"]["def_sacks"] != player["Sacks"]:
                update = 1
            if found_projection["stats"]["def_fumble_rec"] != player["FumblesRecovered"]:
                update = 1    
            if found_projection["stats"]["def_ints"] != player["Interceptions"]:
                update = 1     
            if found_projection["stats"]["def_blk_kicks"] != player["BlockedKicks"]:
                update = 1    
            if found_projection["stats"]["def_safeties"] != player["Safeties"]:
                update = 1    
            if found_projection["stats"]["def_tds_scored"] != player["TouchdownsScored"]:
                update = 1      

            if update == 1:
                player_projections.update_one(
                    {"_id": ObjectId(found_projection["_id"])},
                    {"$set": {
                        "stats.def_pts_allowed": player["PointsAllowed"],
                        "stats.def_sacks": player["Sacks"],
                        "stats.def_fumble_rec": player["FumblesRecovered"],
                        "stats.def_ints": player["Interceptions"],
                        "stats.def_blk_kicks": player["BlockedKicks"],
                        "stats.def_safeties": player["Safeties"],
                        "stats.def_tds_scored": player["TouchdownsScored"],
                        "stats.score": score
                    }}
                )       
                print(f"updated projection for {player["Team"]} for week {projection_week}")
            else:
                print(f"no projection change for {player["Team"]} for week {projection_week}")
                    
        else:
            projection = {}
            projection["player_id"] = player["TeamID"]
            projection["player_name"] = player["Team"] + " Defense"
            projection["team_id"] = player["TeamID"]
            projection["team_abbv"] = player["Team"]
            projection["sport"] = "NFL"
            projection["season"] = projection_season
            projection["week"] = projection_week
            projection["opponent"] = player["Opponent"]
            projection["opponent_team_id"] = player["OpponentID"]
            projection["location"] = player["HomeOrAway"]
            projection["stats"] = {}
            projection["stats"]["pass_yds"] = 0
            projection["stats"]["pass_tds"] = 0
            projection["stats"]["ints"] = 0
            projection["stats"]["rush_yds"] = 0
            projection["stats"]["receptions"] = 0
            projection["stats"]["rec_yds"] = 0
            projection["stats"]["fumbles"] = 0
            projection["stats"]["tds"] = 0
            projection["stats"]["two_pt_conv"] = 0
            projection["stats"]["def_pts_allowed"] = player["PointsAllowed"]
            projection["stats"]["def_sacks"] = player["Sacks"]
            projection["stats"]["def_fumble_rec"] = player["FumblesRecovered"]
            projection["stats"]["def_ints"] = player["Interceptions"]
            projection["stats"]["def_blk_kicks"] = player["BlockedKicks"]
            projection["stats"]["def_safeties"] = player["Safeties"]
            projection["stats"]["def_tds_scored"] = player["TouchdownsScored"]
            projection["stats"]["score"] = score
            projection_inserts.append(projection)
            
            print(f"inserted new projection for {player["Team"]} for week {projection_week}")

    if len(projection_inserts) > 0:
        player_projections.insert_many(projection_inserts)

    return

get_player_projections()