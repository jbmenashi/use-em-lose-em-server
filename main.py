from fastapi import FastAPI, Depends, Request
from dotenv import load_dotenv, find_dotenv
import motor.motor_asyncio
import os
import uvicorn
from beanie import init_beanie
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from auth.db import User, AccessToken
from auth.routers import get_users_router
from auth.users import current_active_user

from routers.league_router import get_league_router
from routers.contestant_router import get_contestant_router
from routers.data_router import get_data_router
from routers.lineup_router import get_lineup_router
from routers.week_router import get_week_router
from routers.matchup_router import get_matchup_router

# import .env variables
load_dotenv(find_dotenv())

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_URI"], uuidRepresentation="standard")
    app.db = app.client.ff_db
    await init_beanie(
        database=app.db,  
        document_models=[
            User,  
            AccessToken
        ]
    )
    yield
    app.client.close()

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:5173",
    "http://localhost"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(get_users_router(app))
app.include_router(get_league_router(app), tags=["league"])
app.include_router(get_contestant_router(app), tags=["contestant"])
app.include_router(get_data_router(app), tags=["data"])
app.include_router(get_lineup_router(app), tags=["lineup"])
app.include_router(get_week_router(app), tags=["week"])
app.include_router(get_matchup_router(app), tags=["matchup"])

def log_cookies(request: Request):
    cookies = request.cookies
    print(f"Cookies: {cookies}")

@app.get("/authenticated-route", tags=["test"])
async def authenticated_route(request: Request, user: User = Depends(current_active_user) ):
    log_cookies(request)
    return {"message": f"Hello {user.email}!"}


