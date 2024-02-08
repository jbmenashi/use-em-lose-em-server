from fastapi import APIRouter, Body, Request, HTTPException, status, Depends
from fastapi.responses import JSONResponse, Response

from auth.users import User, current_active_user
from models.player_model import PlayerModel
from pymongo import ReturnDocument
from beanie import PydanticObjectId

from bson import ObjectId, json_util
import json

def get_player_router(app):

    router = APIRouter()
    
    @router.get("/players", response_description="Get all players for search", response_model_by_alias=False)
    async def get_players(contestant_id: str, filter: dict, request: Request, user: User = Depends(current_active_user)):
        #cursor = request.app.db["Contestants"].find({"user_id": ObjectId(user_id)})
        players = []
        # for con in await cursor.to_list(length=100):
        #     con = json.loads(json_util.dumps(con))
        #     list_of_contestants.append(con)

        return players

    return router
