from pymongo import MongoClient
from bson import ObjectId
import requests
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
import os
from collections import defaultdict

load_dotenv(find_dotenv())

client = MongoClient(os.environ["MONGODB_CONN"])

current_week = 18
current_season = 2023

db = client.ff_db
nfl_game_logs = db["NFLGameLogs"]
player_season_stats = db["PlayerSeasonStats"]
lineups = db["Lineups"]
leagues = db["Leagues"]
matchups = db["Matchups"]

game_log_inserts = []

def get_player_game_logs():
    updated_players = []

    res = requests.get(f"https://api.sportsdata.io/v3/nfl/stats/json/PlayerGameStatsByWeek/{current_season}REG/{current_week}?key=10fd23b6dc3d47f486e1159d2bf02e2b")

    for player in res.json():
        if game_log_exists := nfl_game_logs.find_one({
                "player_id": player["PlayerID"],
                "season": current_season,
                "week": current_week
            }) is not None:
            found_game_log = nfl_game_logs.find_one({
                "player_id": player["PlayerID"],
                "season": current_season,
                "week": current_week
            })
            update = 0
            if found_game_log["pass_yds"] != player["PassingYards"]:
                update = 1
            if found_game_log["pass_tds"] != player["PassingTouchdowns"]:
                update = 1
            if found_game_log["ints"] != player["PassingInterceptions"]:
                update = 1    
            if found_game_log["rush_yds"] != player["RushingYards"]:
                update = 1     
            if found_game_log["receptions"] != player["Receptions"]:
                update = 1    
            if found_game_log["rec_yds"] != player["ReceivingYards"]:
                update = 1    
            if found_game_log["fumbles"] != player["Fumbles"]:
                update = 1    
            if found_game_log["tds"] != player["Touchdowns"]:
                update = 1    
            if found_game_log["yahoo_pts"] != player["FantasyPointsYahoo"]:
                update = 1  

            if update == 1:
                nfl_game_logs.update_one(
                    {"_id": ObjectId(found_game_log["_id"])},
                    {"$set": {
                        "pass_yds": player["PassingYards"],
                        "pass_tds": player["PassingTouchdowns"],
                        "ints": player["PassingInterceptions"],
                        "rush_yds": player["RushingYards"],
                        "receptions": player["Receptions"],
                        "rec_yds": player["ReceivingYards"],
                        "fumbles": player["Fumbles"],
                        "tds": player["Touchdowns"],
                        "yahoo_pts": player["FantasyPointsYahoo"]
                    }}
                )       
                print(f"updated {player["Name"]}")
                updated_players.append(player["PlayerID"])
            else:
                print(f"no change for {player["Name"]}")
                    
        else:
            if player["Position"] in ["QB", "RB", "WR", "TE"] and player["Played"] == 1:
                game_log = {}
                game_log["player_id"] = player["PlayerID"]
                game_log["player_name"] = player["Name"]
                game_log["team_id"] = player["TeamID"]
                game_log["team_abbv"] = player["Team"]
                game_log["season"] = current_season
                game_log["week"] = current_week
                game_log["pass_yds"] = player["PassingYards"]
                game_log["pass_tds"] = player["PassingTouchdowns"]
                game_log["ints"] = player["PassingInterceptions"]
                game_log["rush_yds"] = player["RushingYards"]
                game_log["receptions"] = player["Receptions"]
                game_log["rec_yds"] = player["ReceivingYards"]
                game_log["fumbles"] = player["Fumbles"]
                game_log["tds"] = player["Touchdowns"]
                game_log["two_pt_conv"] = 0
                game_log["def_pts_allowed"] = 0
                game_log["def_sacks"] = 0
                game_log["def_fumble_rec"] = 0
                game_log["def_ints"] = 0
                game_log["def_blk_kicks"] = 0
                game_log["def_safeties"] = 0
                game_log["def_tds_scored"] = 0
                game_log["yahoo_pts"] = player["FantasyPointsYahoo"]
                
                game_log_inserts.append(game_log)
                
                print(f"inserted new game log for {player["Name"]}")
                updated_players.append(player["PlayerID"])

    res = requests.get(f"https://api.sportsdata.io/v3/nfl/stats/json/FantasyDefenseByGame/{current_season}/{current_week}?key=10fd23b6dc3d47f486e1159d2bf02e2b")

    for player in res.json():
        if game_log_exists := nfl_game_logs.find_one({
                "player_id": player["PlayerID"],
                "season": current_season,
                "week": current_week
            }) is not None:
            found_game_log = nfl_game_logs.find_one({
                "player_id": player["PlayerID"],
                "season": current_season,
                "week": current_week
            })
            update = 0
            if found_game_log["def_pts_allowed"] != player["PointsAllowed"]:
                update = 1
            if found_game_log["def_sacks"] != player["Sacks"]:
                update = 1
            if found_game_log["def_fumble_rec"] != player["FumblesRecovered"]:
                update = 1    
            if found_game_log["def_ints"] != player["Interceptions"]:
                update = 1     
            if found_game_log["def_blk_kicks"] != player["BlockedKicks"]:
                update = 1    
            if found_game_log["def_safeties"] != player["Safeties"]:
                update = 1    
            if found_game_log["def_tds_scored"] != player["TouchdownsScored"]:
                update = 1   
            if found_game_log["yahoo_pts"] != player["FantasyPointsYahoo"]:
                update = 1  

            if update == 1:
                nfl_game_logs.update_one(
                    {"_id": ObjectId(found_game_log["_id"])},
                    {"$set": {
                        "def_pts_allowed": player["PointsAllowed"],
                        "def_sacks": player["Sacks"],
                        "def_fumble_rec": player["FumblesRecovered"],
                        "def_ints": player["Interceptions"],
                        "def_blk_kicks": player["BlockedKicks"],
                        "def_safeties": player["Safeties"],
                        "def_tds_scored": player["TouchdownsScored"],
                        "yahoo_pts": player["FantasyPointsYahoo"]
                    }}
                )       
                print(f"updated {player["Team"]}")
                updated_players.append(player["PlayerID"])
            else:
                print(f"no change for {player["Team"]}")
                    
        else:
            game_log = {}
            game_log["player_id"] = player["PlayerID"]
            game_log["player_name"] = player["Team"] + " Defense"
            game_log["team_id"] = player["TeamID"]
            game_log["team_abbv"] = player["Team"]
            game_log["season"] = current_season
            game_log["week"] = current_week
            game_log["pass_yds"] = 0
            game_log["pass_tds"] = 0
            game_log["ints"] = 0
            game_log["rush_yds"] = 0
            game_log["receptions"] = 0
            game_log["rec_yds"] = 0
            game_log["fumbles"] = 0
            game_log["tds"] = 0
            game_log["two_pt_conv"] = 0
            game_log["def_pts_allowed"] = player["PointsAllowed"]
            game_log["def_sacks"] = player["Sacks"]
            game_log["def_fumble_rec"] = player["FumblesRecovered"]
            game_log["def_ints"] = player["Interceptions"]
            game_log["def_blk_kicks"] = player["BlockedKicks"]
            game_log["def_safeties"] = player["Safeties"]
            game_log["def_tds_scored"] = player["TouchdownsScored"]
            game_log["yahoo_pts"] = player["FantasyPointsYahoo"]
            
            game_log_inserts.append(game_log)
            
            print(f"inserted new game log for {player["Team"]}")
            updated_players.append(player["PlayerID"])

    if len(game_log_inserts) > 0:
        nfl_game_logs.insert_many(game_log_inserts)

    return(updated_players)

def season_stats(player_ids):
    new_season_stats = []
    for updated_player_id in player_ids:
        result = db['NFLGameLogs'].aggregate([
            {
                '$match': {
                    'player_id': updated_player_id
                }
            }, {
                '$group': {
                    '_id': '$player_id', 
                    'total_games': {'$sum': 1},
                    'total_pass_yds': { '$sum': '$pass_yds' },
                    'total_pass_tds': { '$sum': '$pass_tds' },
                    'total_ints': { '$sum': '$ints' },
                    'total_rush_yds': { '$sum': '$rush_yds' },
                    'total_receptions': { '$sum': '$receptions' },
                    'total_rec_yds': { '$sum': '$rec_yds' },
                    'total_fumbles': { '$sum': '$fumbles' },
                    'total_tds': { '$sum': '$tds' },
                    'total_two_pt_conv': { '$sum': '$two_pt_conv' },
                    'total_def_pts_allowed': { '$sum': '$def_pts_allowed' },
                    'total_def_sacks': { '$sum': '$def_sacks' },
                    'total_def_fumble_rec': { '$sum': '$def_fumble_rec' },
                    'total_def_ints': { '$sum': '$def_ints' },
                    'total_def_blk_kicks': { '$sum': '$def_blk_kicks' },
                    'total_def_safeties': { '$sum': '$def_safeties' },
                    'total_def_tds_scored': { '$sum': '$def_tds_scored' },
                    'total_yahoo_pts': { '$sum': '$yahoo_pts' }
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
                        "stats.games": result_obj["total_games"],
                        "stats.pass_yds": result_obj["total_pass_yds"],
                        "stats.pass_tds": result_obj["total_pass_tds"],
                        "stats.ints": result_obj["total_ints"],
                        "stats.rush_yds": result_obj["total_rush_yds"],
                        "stats.receptions": result_obj["total_receptions"],
                        "stats.rec_yds": result_obj["total_rec_yds"],
                        "stats.fumbles": result_obj["total_fumbles"],
                        "stats.tds": result_obj["total_tds"],
                        "stats.two_pt_conv": result_obj["total_two_pt_conv"],
                        "stats.def_pts_allowed": result_obj["total_def_pts_allowed"],
                        "stats.def_sacks": result_obj["total_def_sacks"],
                        "stats.def_fumble_rec": result_obj["total_def_fumble_rec"],
                        "stats.def_ints": result_obj["total_def_ints"],
                        "stats.def_blk_kicks": result_obj["total_def_blk_kicks"],
                        "stats.def_safeties": result_obj["total_def_safeties"],
                        "stats.def_tds_scored": result_obj["total_def_tds_scored"],
                        "stats.yahoo_pts": result_obj["total_yahoo_pts"]
                    }}
                )       
                print(f"updated season stats for player {updated_player_id}")           
        else:
            season_stats = {}
            season_stats["player_id"] = updated_player_id
            season_stats["sport"] = "NFL"
            season_stats["season"] = current_season
            season_stats["stats"] = {}
            season_stats["stats"]["games"] = result_obj["total_games"]
            season_stats["stats"]["pass_yds"] = result_obj["total_pass_yds"]
            season_stats["stats"]["pass_tds"] = result_obj["total_pass_tds"]
            season_stats["stats"]["ints"] = result_obj["total_ints"]
            season_stats["stats"]["rush_yds"] = result_obj["total_rush_yds"]
            season_stats["stats"]["receptions"] = result_obj["total_receptions"]
            season_stats["stats"]["rec_yds"] = result_obj["total_rec_yds"]
            season_stats["stats"]["fumbles"] = result_obj["total_fumbles"]
            season_stats["stats"]["tds"] = result_obj["total_tds"]
            season_stats["stats"]["two_pt_conv"] = result_obj["total_two_pt_conv"]
            season_stats["stats"]["def_pts_allowed"] = result_obj["total_def_pts_allowed"]
            season_stats["stats"]["def_sacks"] = result_obj["total_def_sacks"]
            season_stats["stats"]["def_fumble_rec"] = result_obj["total_def_fumble_rec"]        
            season_stats["stats"]["def_ints"] = result_obj["total_def_ints"]        
            season_stats["stats"]["def_blk_kicks"] = result_obj["total_def_blk_kicks"]        
            season_stats["stats"]["def_safeties"] = result_obj["total_def_safeties"]        
            season_stats["stats"]["def_tds_scored"] = result_obj["total_def_tds_scored"]              
            season_stats["stats"]["yahoo_pts"] = result_obj["total_yahoo_pts"]              
            new_season_stats.append(season_stats)
            print(f"Inserting new season stats for player {updated_player_id}")
    
    if len(new_season_stats) > 0:
        player_season_stats.insert_many(new_season_stats)

def update_lineups(playerIds):
    # iterate through list of player IDs
    for player in playerIds:
        print(f"checking lineups for player {player}")
        game_log = nfl_game_logs.find_one({"player_id": player, "week": current_week, "season": current_season})
    # find lineups with that player Id and matches current week
        found_lineups = lineups.find({"selections.player_id": player, "week": current_week, "season": current_season}) # does selections.player_id work?

        for lineup in found_lineups:
            print(f"found selection for {player} in lineup {lineup["_id"]}")
            league = leagues.find_one({"_id": ObjectId(lineup["league_id"])})
            scoring = league["scoring"]["statistics"]

            game_log_fantasy_stats = {}
            for k, v in scoring.items():
                if k == "def_pts_allowed":
                    if game_log[k] == 0:
                        game_log_fantasy_stats[k] = 10
                    elif game_log[k] > 0 and game_log[k] < 7:
                        game_log_fantasy_stats[k] = 7
                    elif game_log[k] >= 7 and game_log[k] < 14:
                        game_log_fantasy_stats[k] = 4
                    elif game_log[k] >= 14 and game_log[k] < 21:
                        game_log_fantasy_stats[k] = 1
                    elif game_log[k] >= 21 and game_log[k] < 28:
                        game_log_fantasy_stats[k] = 0
                    elif game_log[k] >= 28 and game_log[k] < 35:
                        game_log_fantasy_stats[k] = -1
                    else:
                        game_log_fantasy_stats[k] = -4
                else:
                    game_log_fantasy_stats[k] = game_log[k] * v
                # defensive points allowed

            fantasy_stats_dict = { k:v for (k,v) in game_log_fantasy_stats.items()}
            total_points = sum(value for value in game_log_fantasy_stats.values())

            selection_index = next((i for i, item in enumerate(lineup["selections"]) if item["player_id"] == player))

            lineup_score = 0
            for selection in lineup["selections"]:
                if selection["index"] != selection_index:
                    lineup_score += selection["score"]

            lineup_score += total_points

            if "fantasy_stats" not in lineup["selections"][selection_index].keys():
                print("first game log for player")

                lineups.update_one(
                    {"_id": ObjectId(lineup["_id"])},
                    {
                        "$push": { 
                            f"selections.{selection_index}.fantasy_stats": fantasy_stats_dict,
                            f"selections.{selection_index}.total_points": total_points
                        },
                        "$set": { 
                            f"selections.{selection_index}.locked": True,
                            f"score": lineup_score
                        }
                    }
                )   
            else:
                lineups.update_one(
                    {"_id": ObjectId(lineup["_id"])},
                    {
                        "$set": { 
                            f"selections.{selection_index}.fantasy_stats": fantasy_stats_dict,
                            f"selections.{selection_index}.total_points": total_points,
                            f"score": lineup_score
                        }
                    }
                )  

            found_matchup = matchups.find_one({"team_1_id": ObjectId(lineup["contestant_id"]), "season": current_season, "week": current_week})  

            if found_matchup:
                matchups.update_one(
                    {"_id": ObjectId(found_matchup["_id"])},
                    {
                        "$set": { 
                            f"team_1_score": lineup_score
                        }
                    }
                )  
            else:
                found_matchup_two = matchups.find_one({"team_2_id": ObjectId(lineup["contestant_id"]), "season": current_season, "week": current_week}) 
                matchups.update_one(
                    {"_id": ObjectId(found_matchup_two["_id"])},
                    {
                        "$set": { 
                            f"team_2_score": lineup_score
                        }
                    }
                )   
    
    return

players = get_player_game_logs()
season_stats(players)
# update_lineups(players)

