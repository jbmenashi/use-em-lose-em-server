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

def update_standings():
    # get all leagues that are active
    active_leagues = leagues.find({"active": True})

    for league in active_leagues:
        print(league["_id"])

    # in each league, get all matchups that are finished

    # 
    return

update_standings()