from fastapi import APIRouter, Body, Request, HTTPException, status, Depends
from fastapi.responses import JSONResponse, Response

from auth.users import User, current_active_user
from models.contestant_model import ContestantModel, UpdateContestantModel
from pymongo import ReturnDocument
from beanie import PydanticObjectId

from bson import ObjectId, json_util
import json

def get_contestant_router(app):

    router = APIRouter()

    @router.post("/contestant/{league_id}", response_description="Create a Contestant (add Contestant to League)", status_code=status.HTTP_201_CREATED, response_model_by_alias=False)
    async def create_contestant(league_id: str,  request: Request, user: User = Depends(current_active_user), team_name: str | None = None):
        if (
            league_to_join := await request.app.db["Leagues"].find_one({"_id": ObjectId(league_id)})
        ) is not None:
            # get the # of contestants in the league
            league_size = league_to_join["size"]

            # make sure there is space in the league by checking number of contestants currently in the league
            cursor = request.app.db["Contestants"].find({"league_id": ObjectId(league_id)})
            contestants_count = 0
            for con in await cursor.to_list(length=100):
                contestants_count = contestants_count + 1

            if contestants_count >= league_size:
                raise HTTPException(status_code=400, detail=f"League is full")
            
            # make sure user isn't in the league already
            if (
                already_in_league := await request.app.db["Contestants"].find_one(
                    {
                        "$and": [
                            {"league_id": ObjectId(league_id)},
                            {"user_id": ObjectId(user.id)}
                        ]
                    }
                )
            ) is not None:
                raise HTTPException(status_code=400, detail=f"User is already in this league")
            
            contestant = ContestantModel(locked=False, team_name=team_name)

            new_contestant = await request.app.db["Contestants"].insert_one(
            contestant.model_dump(by_alias=True)
            )
            created_contestant = await request.app.db["Contestants"].find_one_and_update(
                {"_id": new_contestant.inserted_id}, {"$set": {"user_id": user.id, "league_id": ObjectId(league_id)}}, return_document=ReturnDocument.AFTER
            )

            if contestants_count + 1 == league_size:
                league_to_update = await request.app.db["Leagues"].find_one_and_update(
                {"_id": ObjectId(league_id)}, {"$set": {"full": True}}, return_document=ReturnDocument.AFTER
                )    

            res = {}
            res["contestant"] = created_contestant

            return json.loads(json_util.dumps(res))
            
        raise HTTPException(status_code=404, detail=f"League {league_id} not found")
    
    @router.get("/contestant/{id}", response_description="Get a single contestant", response_model=ContestantModel, response_model_by_alias=False)
    async def get_contestant(id: str, request: Request, user: User = Depends(current_active_user)):
        if (
            contestant := await request.app.db["Contestants"].find_one({"_id": ObjectId(id)})
        ) is not None:
            return contestant
        raise HTTPException(status_code=404, detail=f"Contestant {id} not found")
    
    @router.get("/contestant/user/{user_id}", response_description="Get all contestants belonging to a user", response_model_by_alias=False)
    async def get_contestant_by_user(user_id: str, request: Request, user: User = Depends(current_active_user)):
        cursor = request.app.db["Contestants"].aggregate(
            [
                {
                    '$match': {
                        'user_id': ObjectId(user_id)
                    }
                },
                {
                    '$lookup': {
                        'from': 'Leagues',
                        'localField': 'league_id',
                        'foreignField': '_id',
                        'as': 'league_info'
                    }
                },
                {
                    '$unwind': '$league_info'
                },
                {
                    '$project': {
                        '_id': 1,
                        'user_id': 1,
                        'league_id': 1,
                        'team_name': 1,
                        'locked': 1,
                        'league_name': '$league_info.league_name',
                        'commissioner_id': '$league_info.commissioner',
                        'sport': '$league_info.sport',
                        'style': '$league_info.style',
                        'league_locked': '$league_info.locked',
                        'league_active': '$league_info.active',
                    }
                }
            ]
        )

        list_of_contestants = []
        for con in await cursor.to_list(length=100):
            con = json.loads(json_util.dumps(con))
            con["contestant_id"] = str(con["_id"]["$oid"])
            con["league_id"] = str(con["league_id"]["$oid"])
            con["user_id"] = str(con["user_id"]["$oid"])
            con["commissioner_id"] = str(con["commissioner_id"]["$oid"])
            list_of_contestants.append(con)

        return list_of_contestants
    
    @router.get("/test/", response_description="Get all contestants belonging to a user", response_model_by_alias=False)
    async def get_contestant_test(request: Request, user: User = Depends(current_active_user)):
        return None
    
    @router.get("/contestant/league/{league_id}", response_description="Get all contestants belonging to a league", response_model_by_alias=False)
    async def get_contestant_by_league(league_id: str, request: Request, user: User = Depends(current_active_user)):
        cursor = request.app.db["Contestants"].find({"league_id": ObjectId(league_id)})
        list_of_contestants = []
        for con in await cursor.to_list(length=100):
            con = json.loads(json_util.dumps(con))
            list_of_contestants.append(con)

        return list_of_contestants

    @router.put("/contestant/{id}", response_description="Update a contestant", response_model=ContestantModel, response_model_by_alias=False)
    async def update_contestant(id: str, request: Request, user: User = Depends(current_active_user), contestant: UpdateContestantModel = Body(...)):
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

    @router.delete("/contestant/{id}", response_description="Delete contestant")
    async def delete_contestant(id: str, request: Request, user: User = Depends(current_active_user)):
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

                    league_to_update = await request.app.db["Leagues"].find_one_and_update(
                        {"_id": ObjectId(existing_contestant["league_id"])}, {"$set": {"full": False}}, return_document=ReturnDocument.AFTER
                    )   

                if delete_result.deleted_count == 1:
                    return Response(status_code=status.HTTP_204_NO_CONTENT) 
            
            else:
                raise HTTPException(status_code=401, detail=f"Not authorized to delete contestant {id}")                           

        raise HTTPException(status_code=404, detail=f"contestant {id} not found")

    return router
