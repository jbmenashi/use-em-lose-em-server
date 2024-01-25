from fastapi import FastAPI, Depends
from dotenv import load_dotenv, find_dotenv
import motor.motor_asyncio
import os
import uvicorn
from beanie import init_beanie
from contextlib import asynccontextmanager

from auth.db import User, AccessToken
from auth.routers import get_users_router
from auth.users import current_active_user

# import .env variables
load_dotenv(find_dotenv())

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_CONN"], uuidRepresentation="standard")
    app.db = app.client.ff_db
    await init_beanie(
        database=app.db,  
        document_models=[
            User,  
            AccessToken
        ]
    )

    app.include_router(get_users_router(app))

    @app.get("/authenticated-route", tags=["test"])
    async def authenticated_route(user: User = Depends(current_active_user)):
        return {"message": f"Hello {user.email}!"}

    yield
    app.client.close()

app = FastAPI(lifespan=lifespan)



