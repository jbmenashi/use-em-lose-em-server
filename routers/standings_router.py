from fastapi import APIRouter, Body, Request, HTTPException, status, Depends
from fastapi.responses import JSONResponse, Response

from auth.users import User, current_active_user
from models.standings_model import StandingsModel
from pymongo import ReturnDocument
from beanie import PydanticObjectId

from bson import ObjectId, json_util
import json

def get_standings_router(app):

    router = APIRouter()
    
    @router.get("/standings/{league_id}", response_description="Get standings for league_id", response_model_by_alias=False)
    async def get_standings(league_id: str, filter: dict, request: Request, user: User = Depends(current_active_user)):
        #cursor = request.app.db["Contestants"].find({"user_id": ObjectId(user_id)})
        standings = []
        # for con in await cursor.to_list(length=100):
        #     con = json.loads(json_util.dumps(con))
        #     list_of_contestants.append(con)

        return standings

    return router
