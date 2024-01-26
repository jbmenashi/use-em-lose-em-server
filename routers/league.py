from fastapi import APIRouter, Body, Request, HTTPException, status, Depends
from fastapi.responses import JSONResponse, Response

from auth.users import User, current_active_user
from models.league import LeagueModel, UpdateLeagueModel
from pymongo import ReturnDocument

from bson import ObjectId, json_util
import json

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

def get_league_router(app):

    router = APIRouter()

    @router.post("/league/", response_description="Add new league", status_code=status.HTTP_201_CREATED, response_model_by_alias=False)
    async def create_league(request: Request, user: User = Depends(current_active_user), league: LeagueModel = Body(...)):
        new_league = await request.app.db["Leagues"].insert_one(
            league.model_dump(by_alias=True)
        )
        created_league = await request.app.db["Leagues"].find_one_and_update(
            {"_id": new_league.inserted_id}, {"$set": {"commissioner": user.id}}, return_document=ReturnDocument.AFTER
        )

        if created_league:
            contestant = {
                "user_id": user.id,
                "league_id": created_league["_id"]
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

    @router.put("/league/{id}", response_description="Update a league", response_model=LeagueModel, response_model_by_alias=False)
    async def update_league(id: str, request: Request, user: User = Depends(current_active_user), league: UpdateLeagueModel = Body(...)):
        league = {
        k: v for k, v in league.model_dump(by_alias=True).items() if v is not None
        }

        if len(league) >= 1:
            update_result = await request.app.db["Leagues"].find_one_and_update(
                {"_id": ObjectId(id)}, {"$set": league}, return_document=ReturnDocument.AFTER
            )
            print(update_result)
            if update_result is not None:
                return update_result
            else:
                raise HTTPException(status_code=404, detail=f"League {id} not found")

        if (existing_league := await request.app.db["Leagues"].find_one({"_id": ObjectId(id)})) is not None:
            return existing_league

        raise HTTPException(status_code=404, detail=f"Student {id} not found")

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
