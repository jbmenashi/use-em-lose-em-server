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
    
    @router.get("/players/{contestant_id}", response_description="Get all players for search", response_model_by_alias=False)
    async def get_players(
        contestant_id: str, 
        request: Request, 
        page: int = 1, 
        limit: int = 25, 
        position_filter: str | None = None, 
        team_filter: str | None = None,
        sort_category: str | None = None,
        user: User = Depends(current_active_user)):
        if (existing_contestant := await request.app.db["Contestants"].find_one({"_id": ObjectId(contestant_id)})) is not None:
            unavail_player_ids = []
            unavail_team_ids = []

            for player in existing_contestant["unavailable_players"]:
                unavail_player_ids.append(player["player_id"])

            for team in existing_contestant["unavailable_teams"]:
                unavail_team_ids.append(team["team_id"])

            find_query = {
                        "status": "Active",
                        "player_id": {"$nin": unavail_player_ids},
                        "team_id": {"$nin": unavail_team_ids}                
            }

            if position_filter is not None:
                if position_filter == "C":
                    find_query["position"] = position_filter
                elif position_filter == "IF":
                    find_query["position_category"] = position_filter
                    find_query["position"] = { "$ne": "C" }
                else:
                    find_query["position_category"] = position_filter

            if team_filter is not None:
                find_query["team_abbreviation"] = team_filter

            if sort_category:
                if sort_category == "H":
                    sort_query = {"season_hits": -1}
                elif sort_category == "HR":
                    sort_query = {"season_home_runs": -1}
                elif sort_category == "RBI":
                    sort_query = {"season_runs_batted_in": -1}
            else:
                sort_query = {"season_hits": -1}

            results = await request.app.db["MLBPlayerSearchView"].find(find_query).sort(sort_query).skip((page - 1) * limit).limit(limit).to_list(length=limit)

            return json.loads(json_util.dumps(results))

        raise HTTPException(status_code=404, detail=f"Contestant {contestant_id} not found")

    return router
