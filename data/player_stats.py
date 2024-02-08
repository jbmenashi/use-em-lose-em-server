from pymongo import MongoClient
from bson import ObjectId
import requests
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

client = MongoClient(os.environ["MONGODB_CONN"])

game_date = "2023-APR-02"
current_week = 1
current_season = 2023

db = client.ff_db
player_game_logs = db["PlayerGameLogs"]
player_season_stats = db["PlayerSeasonStats"]

game_log_inserts = []

def get_player_game_logs():
    res = requests.get(f"https://api.sportsdata.io/v3/mlb/stats/json/PlayerGameStatsByDate/{game_date}?key=e83af77dbf8849018751c5366a98e164")

    updated_players = []

    for player in res.json():
        if game_log_exists := player_game_logs.find_one({
                "player_id": player["PlayerID"],
                "game_date": game_date
            }) is not None:
            found_game_log = player_game_logs.find_one({
                "player_id": player["PlayerID"],
                "game_date": game_date
            })
            update = 0
            if found_game_log["hits"] != player["Hits"]:
                update = 1
            if found_game_log["home_runs"] != player["HomeRuns"]:
                update = 1
            if found_game_log["runs_batted_in"] != player["RunsBattedIn"]:
                update = 1    

            if update == 1:
                player_game_logs.update_one(
                    {"_id": ObjectId(found_game_log["_id"])},
                    {"$set": {
                        "hits": player["Hits"],
                        "home_runs": player["HomeRuns"],
                        "runs_batted_in": player["RunsBattedIn"]
                    }}
                )       
                print(f"updated {player["Name"]}")
                updated_players.append(player["PlayerID"])
            else:
                print(f"no change for {player["Name"]}")
                    
        else:
            if player["PositionCategory"] != "P":
                game_log = {}
                game_log["player_id"] = player["PlayerID"]
                game_log["player_name"] = player["Name"]
                game_log["team_id"] = player["TeamID"]
                game_log["team_abbv"] = player["Team"]
                game_log["game_date"] = game_date
                # if player["isGameOver"]:
                #     game_log["active"] = False
                # else:
                #     game_log["active"] = True
                game_log["hits"] = player["Hits"]
                game_log["home_runs"] = player["HomeRuns"]
                game_log["runs_batted_in"] = player["RunsBattedIn"]
                game_log_inserts.append(game_log)
                
                print(f"inserted new game log for {player["Name"]}")
                updated_players.append(player["PlayerID"])

    if len(game_log_inserts) > 0:
        player_game_logs.insert_many(game_log_inserts)

    return(updated_players)

def season_stats(player_ids):
    new_season_stats = []
    for updated_player_id in player_ids:
        result = db['PlayerGameLogs'].aggregate([
            {
                '$match': {
                    'player_id': updated_player_id
                }
            }, {
                '$group': {
                    '_id': '$player_id', 
                    'total_hits': {
                        '$sum': '$hits'
                    },
                    'total_home_runs': {
                        '$sum': '$home_runs'
                    },
                    'total_runs_batted_in': {
                        '$sum': '$runs_batted_in'
                    }
                }
            }
        ])

        result_obj = list(result)[0]

        if season_stat_exists := player_season_stats.find_one({
            "player_id": updated_player_id,
            "season": current_season
            }) is not None:
                found_season_stat = player_season_stats.find_one({
                "player_id": updated_player_id,
                "season": current_season
                })
                player_season_stats.update_one(
                    {"_id": ObjectId(found_season_stat["_id"])},
                    {"$set": {
                        "hits": result_obj["total_hits"],
                        "home_runs": result_obj["total_home_runs"],
                        "runs_batted_in": result_obj["total_runs_batted_in"]
                    }}
                )       
                print(f"updated season stats for player {updated_player_id}")           
        else:
            season_stats = {}
            season_stats["player_id"] = updated_player_id
            season_stats["season"] = current_season
            season_stats["stats"] = {}
            season_stats["stats"]["hits"] = result_obj["total_hits"]
            season_stats["stats"]["home_runs"] = result_obj["total_home_runs"]
            season_stats["stats"]["runs_batted_in"] = result_obj["total_runs_batted_in"]
            new_season_stats.append(season_stats)
            print(f"Inserting new season stats for player {updated_player_id}")
    
    if len(new_season_stats) > 0:
        player_season_stats.insert_many(new_season_stats)

def update_lineups(playerIds):
    # iterate through list of player IDs
    # find lineups with that player Id and matches current week
    # update stats for the player inside the lineup by summing up relevant game logs
    return

players = get_player_game_logs()
season_stats(players)
update_lineups(players)

