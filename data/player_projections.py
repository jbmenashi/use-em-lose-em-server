from pymongo import MongoClient
from bson import ObjectId
import requests
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

client = MongoClient(os.environ["MONGODB_CONN"])

def update_standings():
    return

update_standings()