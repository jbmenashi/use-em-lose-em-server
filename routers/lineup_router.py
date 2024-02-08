from fastapi import APIRouter, Body, Request, HTTPException, status, Depends
from fastapi.responses import JSONResponse, Response

from auth.users import User, current_active_user
from models.lineup_model import LineupModel, UpdateLineupModel
from pymongo import ReturnDocument
from beanie import PydanticObjectId

from bson import ObjectId, json_util
import json

def get_lineup_router(app):

    router = APIRouter()

    @router.post("/lineup/{contestant_id}", response_description="Create a Lineup (add Lineup to Contestant)", response_model=LineupModel, status_code=status.HTTP_201_CREATED, response_model_by_alias=False)
    async def create_lineup(contestant_id: str, request: Request, user: User = Depends(current_active_user)):
        return
    
    @router.get("/lineup/{id}", response_description="Get a single lineup", response_model=LineupModel, response_model_by_alias=False)
    async def get_lineup(id: str, request: Request, user: User = Depends(current_active_user)):
        if (
            lineup := await request.app.db["Lineups"].find_one({"_id": ObjectId(id)})
        ) is not None:
            return lineup
        raise HTTPException(status_code=404, detail=f"Lineup {id} not found")
    
    @router.get("/lineup/league/{league_id}", response_description="Get all lineups belonging to a league", response_model_by_alias=False)
    async def get_lineup_by_league(league_id: str, request: Request, user: User = Depends(current_active_user)):
        cursor = request.app.db["Contestants"].find({"league_id": ObjectId(league_id)})
        list_of_contestants = []
        for con in await cursor.to_list(length=100):
            con = json.loads(json_util.dumps(con))
            list_of_contestants.append(con)

        return list_of_contestants

    @router.put("/lineup/{id}", response_description="Update a lineup", response_model=LineupModel, response_model_by_alias=False)
    async def update_lineup(id: str, request: Request, user: User = Depends(current_active_user), lineup: UpdateLineupModel = Body(...)):
        if (existing_contestant := await request.app.db["Contestants"].find_one({"_id": ObjectId(id)})) is not None:
            if existing_contestant["user_id"] == user.id:
                if existing_contestant["locked"] == False:
                    contestant = { k: v for k, v in contestant.model_dump(by_alias=True).items() if v is not None }      

                    if len(contestant) >= 1:
                        update_result = await request.app.db["Contestants"].find_one_and_update(
                            {"_id": ObjectId(id)}, {"$set": contestant}, return_document=ReturnDocument.AFTER
                        )
                        return update_result
                    else:
                        return existing_contestant
                else:
                    raise HTTPException(status_code=400, detail=f"Contestant is locked for changes")
            else:
                raise HTTPException(status_code=401, detail=f"Not authorized to edit Contestant {id}")

        raise HTTPException(status_code=404, detail=f"Contestant {id} not found")

    @router.delete("/lineup/{id}", response_description="Delete lineup")
    async def delete_lineup(id: str, request: Request, user: User = Depends(current_active_user)):
        # Does contestant exist
        if (existing_contestant := await request.app.db["Contestants"].find_one({"_id": ObjectId(id)})) is not None:
            # Does the user id on the contestant match the user id of the requester
            if existing_contestant["user_id"] == user.id:
                # then delete the contestant
                delete_result = await request.app.db["Contestants"].delete_one({"_id": ObjectId(id)})

                # if the user/contestant is also the commissioner of the league
                #print(existing_contestant["league_id"])
                if (
                    con_is_commissh := await request.app.db["Leagues"].find_one(
                    {
                        "$and": [
                            {"_id": ObjectId(existing_contestant["league_id"])},
                            {"commissioner": ObjectId(user.id)}
                        ]
                    }
                )
                ) is not None:
                    print("here")
                    # Delete all contestants with the contestant ID
                    cursor = request.app.db["Contestants"].find({"league_id": ObjectId(existing_contestant["league_id"])})
                    for document in await cursor.to_list(length=100):
                        delete_contestants = await request.app.db["Contestants"].delete_one({"_id": document["_id"]})   
                    # and then delete the league
                    delete_league_result = await request.app.db["Leagues"].delete_one({"_id": ObjectId(existing_contestant["league_id"])})    

                if delete_result.deleted_count == 1:
                    return Response(status_code=status.HTTP_204_NO_CONTENT) 
            
            else:
                raise HTTPException(status_code=401, detail=f"Not authorized to delete contestant {id}")                           

        raise HTTPException(status_code=404, detail=f"contestant {id} not found")

    return router
