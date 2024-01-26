from fastapi import APIRouter, Body, Request, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from auth.users import User, current_active_user
from models.league import LeagueModel, UpdateLeagueModel

from bson import ObjectId, json_util
import json

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

def get_league_router(app):

    router = APIRouter()

    @router.post(
        "/league/",
        response_description="Add new league",
        #response_model=LeagueModel,
        status_code=status.HTTP_201_CREATED,
        response_model_by_alias=False,
    )
    async def create_league(
        request: Request,
        user: User = Depends(current_active_user),
        league: LeagueModel = Body(...),
    ):
        league = jsonable_encoder(league)
        new_league = await request.app.db["Leagues"].insert_one(league)
        created_league = await request.app.db["Leagues"].find_one(
            {"_id": new_league.inserted_id}
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
    
    @router.get(
        "/league/{id}",
        response_description="Get a single league",
        response_model=LeagueModel,
        response_model_by_alias=False,
    )
    async def get_league(
        id: str,
        request: Request,          
        user: User = Depends(current_active_user), 
    ):
        if (
            league := await request.app.db["Leagues"].find_one({"_id": ObjectId(id)})
        ) is not None:
            return league
        raise HTTPException(status_code=404, detail=f"League {id} not found")
    
    # @router.get("/", response_description="List all tasks")
    # async def list_tasks(
    #     request: Request,
    #     user: User = Depends(app.fastapi_users.get_current_active_user),
    # ):
    #     tasks = []
    #     for doc in await request.app.db["tasks"].find().to_list(length=100):
    #         tasks.append(doc)
    #     return tasks

    # @router.put("/{id}", response_description="Update a task")
    # async def update_task(
    #     id: str,
    #     request: Request,
    #     user: User = Depends(app.fastapi_users.get_current_active_user),
    #     task: UpdateTaskModel = Body(...),
    # ):
    #     task = {k: v for k, v in task.dict().items() if v is not None}

    #     if len(task) >= 1:
    #         update_result = await request.app.db["tasks"].update_one(
    #             {"_id": id}, {"$set": task}
    #         )

    #         if update_result.modified_count == 1:
    #             if (
    #                 updated_task := await request.app.db["tasks"].find_one({"_id": id})
    #             ) is not None:
    #                 return updated_task

    #     if (
    #         existing_task := await request.app.db["tasks"].find_one({"_id": id})
    #     ) is not None:
    #         return existing_task

    #     raise HTTPException(status_code=404, detail=f"Task {id} not found")

    # @router.delete("/{id}", response_description="Delete Task")
    # async def delete_task(
    #     id: str,
    #     request: Request,
    #     user: User = Depends(app.fastapi_users.get_current_active_user),
    # ):
    #     delete_result = await request.app.db["tasks"].delete_one({"_id": id})

    #     if delete_result.deleted_count == 1:
    #         return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)

    #     raise HTTPException(status_code=404, detail=f"Task {id} not found")

    return router
