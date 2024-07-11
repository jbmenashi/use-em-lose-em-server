from pymongo import MongoClient
from bson import ObjectId
import requests
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

client = MongoClient(os.environ["MONGODB_CONN"])
db = client.ff_db
# teams = db["Teams"]
playerDetails = db["PlayerDetails"]

def get_player_details():
    docs = []

    res = requests.get("https://api.sportsdata.io/v3/nfl/scores/json/Teams?key=10fd23b6dc3d47f486e1159d2bf02e2b")

    for team in res.json():
        doc = {}
        doc["sport"] = "NFL"
        doc["player_id"] = team["TeamID"]
        doc["first_name"] = team["Key"]
        doc["last_name"] = "Defense"
        doc["status"] = "Active"
        doc["team_id"] = team["TeamID"]
        doc["team_abbreviation"] = team["Key"]
        doc["jersey_num"] = 0
        doc["position_category"] = "DEF"
        doc["position"] = "DEF"

        # doc["sport"] = "NFL"
        # doc["team_id"] = team["TeamID"]
        # doc["city"] = team["City"]
        # doc["nickname"] = team["Name"]
        # doc["abbreviation"] = team["Key"]
        # doc["subleague"] = team["Conference"]
        # doc["division"] = team["Division"]
        # doc["primary_color"] = team["PrimaryColor"]
        # doc["secondary_color"] = team["SecondaryColor"]
        # doc["tertiary_color"] = team["TertiaryColor"]
        docs.append(doc)
        print(f"inserted {team["City"]}")

    if len(docs) > 0:
        playerDetails.insert_many(docs) 

get_player_details()