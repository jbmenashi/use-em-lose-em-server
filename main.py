from fastapi import FastAPI
from dotenv import load_dotenv, find_dotenv
import motor.motor_asyncio
import os
import uvicorn

load_dotenv(find_dotenv())
client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_CONN"])

app = FastAPI()