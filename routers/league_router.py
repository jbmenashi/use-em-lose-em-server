from fastapi import APIRouter, Body, Request, HTTPException, status, Depends
from fastapi.responses import JSONResponse, Response

from auth.users import User, current_active_user
from models.league_model import LeagueModel, UpdateLeagueModel
from pymongo import ReturnDocument

from bson import ObjectId, json_util
import json

def get_league_router(app):

    router = APIRouter()

    @router.post("/league/", response_description="Add new league", status_code=status.HTTP_201_CREATED, response_model_by_alias=False)
    async def create_league(request: Request, user: User = Depends(current_active_user), league: LeagueModel = Body(...)):
        team_name = league.team_name
        del league.team_name

        new_league = await request.app.db["Leagues"].insert_one(
            league.model_dump(by_alias=True)
        )
        created_league = await request.app.db["Leagues"].find_one_and_update(
            {"_id": new_league.inserted_id}, {"$set": {"commissioner": user.id}}, return_document=ReturnDocument.AFTER
        )

        if created_league:
            contestant = {
                "user_id": user.id,
                "league_id": created_league["_id"],
                "team_name": team_name,
                "unavailable_players": [],
                "unavailable_teams": [],
                "team_count": {},
                "locked": False
            }
            new_contestant = await request.app.db["Contestants"].insert_one(contestant)
            created_contestant = await request.app.db["Contestants"].find_one(
            {"_id": new_contestant.inserted_id}
        )
            
        res = {}
        res["league"] = created_league
        res["contestant"] = created_contestant

        return json.loads(json_util.dumps(res))
    
    @router.get("/league/{id}", response_description="Get a single league", response_model=LeagueModel, response_model_by_alias=False)
    async def get_league(id: str, request: Request, user: User = Depends(current_active_user)):
        if (
            league := await request.app.db["Leagues"].find_one({"_id": ObjectId(id)})
        ) is not None:
            return league
        raise HTTPException(status_code=404, detail=f"League {id} not found")
    
    @router.get("/league/available/{user_id}", response_description="Get available leagues to join for a user", response_model_by_alias=False)
    async def get_league(user_id: str, request: Request, user: User = Depends(current_active_user)):
        list_of_leagues = []
        cursor = request.app.db["Leagues"].find({'$and': [{"locked": False},{"active": False}]})
        for league in await cursor.to_list(length=100):
            con_cursor = request.app.db["Contestants"].find({'$and': [{"league_id": ObjectId(league["_id"])},{"user_id": ObjectId(user_id)}]})
            con_list = await con_cursor.to_list(length=100)
            if len(con_list) == 0:
                list_of_leagues.append(json.loads(json_util.dumps(league)))

        return list_of_leagues

    @router.put("/league/{id}", response_description="Update a league", response_model=LeagueModel, response_model_by_alias=False)
    async def update_league(id: str, request: Request, user: User = Depends(current_active_user), league: UpdateLeagueModel = Body(...)):
        if (existing_league := await request.app.db["Leagues"].find_one({"_id": ObjectId(id)})) is not None:
            if existing_league["commissioner"] == user.id:
                if existing_league["locked"] == False:
                    league = { k: v for k, v in league.model_dump(by_alias=True).items() if v is not None }      

                    if len(league) >= 1:
                        update_result = await request.app.db["Leagues"].find_one_and_update(
                            {"_id": ObjectId(id)}, {"$set": league}, return_document=ReturnDocument.AFTER
                        )

                        if league["locked"]:
                            cursor = request.app.db["Contestants"].find({"league_id": ObjectId(id)})
                            for con in await cursor.to_list(length=100):
                                update_contestant = await request.app.db["Contestants"].find_one_and_update(
                                    {"_id": ObjectId(con["_id"])}, {"$set": {"locked": True}}
                                )

                        return update_result
                    else:
                        return existing_league
                else:
                    raise HTTPException(status_code=400, detail=f"League is locked for changes")
            else:
                raise HTTPException(status_code=401, detail=f"Not authorized to edit League {id}")

        raise HTTPException(status_code=404, detail=f"League {id} not found")

    @router.delete("/league/{id}", response_description="Delete League")
    async def delete_league(id: str, request: Request, user: User = Depends(current_active_user)):
        if (existing_league := await request.app.db["Leagues"].find_one({"_id": ObjectId(id)})) is not None:
            if existing_league["commissioner"] == user.id:
                
                # Delete all contestants with the league ID
                cursor = request.app.db["Contestants"].find({"league_id": ObjectId(id)})
                for document in await cursor.to_list(length=100):
                    delete_contestants = await request.app.db["Contestants"].delete_one({"_id": document["_id"]})

                delete_result = await request.app.db["Leagues"].delete_one({"_id": ObjectId(id)})
                if delete_result.deleted_count == 1:
                    return Response(status_code=status.HTTP_204_NO_CONTENT)             
            else:
                raise HTTPException(status_code=401, detail=f"Not authorized to delete League {id}")
            

        raise HTTPException(status_code=404, detail=f"League {id} not found")

    return router
