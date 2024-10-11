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

    @router.post("/lineup/{contestant_id}", response_description="Create a Lineup (add Lineup to Contestant)", status_code=status.HTTP_201_CREATED, response_model_by_alias=False)
    async def create_lineup(contestant_id: str, request: Request, user: User = Depends(current_active_user), lineup: LineupModel = Body(...)):
        if (existing_contestant := await request.app.db["Contestants"].find_one({"_id": ObjectId(contestant_id)})) is not None:
            if existing_contestant["user_id"] == user.id:
                new_lineup = await request.app.db["Lineups"].insert_one(lineup.model_dump(by_alias=True))

                lineup_league = await request.app.db["Leagues"].find_one({"_id": ObjectId(existing_contestant["league_id"])})

                selections = []
                for key, value in lineup_league["roster"]["positions"].items():
                    selections.extend([key] * value)
                
                selections = [{"position": item, "locked": False, "index": index} for index, item in enumerate(selections)]

                created_lineup = await request.app.db["Lineups"].find_one_and_update(
                    {"_id": new_lineup.inserted_id}, {"$set": {"contestant_id": ObjectId(contestant_id), "league_id": ObjectId(existing_contestant["league_id"]), "selections": selections}}, return_document=ReturnDocument.AFTER
                )

                res = {}
                res["lineup"] = created_lineup

                return json.loads(json_util.dumps(res))
            
            raise HTTPException(status_code=401, detail=f"Not authorized to create lineup for this contestant")
        raise HTTPException(status_code=404, detail=f"Contestant {contestant_id} not found")
    
    @router.get("/lineup/{id}", response_description="Get a single lineup", response_model=LineupModel, response_model_by_alias=False)
    async def get_lineup(id: str, request: Request, user: User = Depends(current_active_user)):
        if (
            lineup := await request.app.db["Lineups"].find_one({"_id": ObjectId(id)})
        ) is not None:
            return lineup
        raise HTTPException(status_code=404, detail=f"Lineup {id} not found")
    
    @router.get("/lineup/league/{league_id}", response_description="Get all lineups belonging to a league", response_model_by_alias=False)
    async def get_lineup_by_league(league_id: str, request: Request, user: User = Depends(current_active_user)):
        cursor = request.app.db["Lineups"].find({"league_id": ObjectId(league_id)})
        list_of_lineups = []
        for con in await cursor.to_list(length=100):
            con = json.loads(json_util.dumps(con))
            list_of_lineups.append(con)

        return list_of_lineups
    
    @router.get("/lineup/contestant/{contestant_id}", response_description="Get week lineup belonging to a contestant", response_model_by_alias=False)
    async def get_lineup_by_contestant(contestant_id: str, request: Request, week: int = 1, user: User = Depends(current_active_user)):
        existing_lineup = await request.app.db["Lineups"].find_one({"contestant_id": ObjectId(contestant_id), "week": week})

        if existing_lineup is not None:
            return json.loads(json_util.dumps(existing_lineup))
        else:
            raise HTTPException(status_code=404, detail=f"Lineup not found")

    @router.put("/lineup/{id}", response_description="Update a lineup", response_model_by_alias=False)
    async def update_lineup(id: str, request: Request, user: User = Depends(current_active_user), selection: dict = {}):
        print(selection)
        if (existing_lineup := await request.app.db["Lineups"].find_one({"_id": ObjectId(id)})) is not None:
            lineup_contestant = await request.app.db["Contestants"].find_one({"_id": ObjectId(existing_lineup["contestant_id"])})
            lineup_league = await request.app.db["Leagues"].find_one({"_id": ObjectId(existing_lineup["league_id"])})
            league_team_count = lineup_league['team_count']

            if lineup_contestant["user_id"] == user.id and existing_lineup["locked"] == False:
                for sel in existing_lineup["selections"]:
                    if sel["index"] == selection["index"] and sel["position"].upper() == selection["position"].upper():
                        if sel["locked"] == False:
                            updated_lineup = await request.app.db["Lineups"].find_one_and_update(
                                {"_id": ObjectId(id)}, 
                                {"$set": {
                                    f"selections.{selection["index"]}.player_id": selection["player_id"],
                                    f"selections.{selection["index"]}.player_name": selection["player_name"],
                                    f"selections.{selection["index"]}.team_id": selection["team_id"],
                                    f"selections.{selection["index"]}.team_abbreviation": selection["team_abbreviation"],
                                    f"selections.{selection["index"]}.opponent": selection["opponent"],
                                    f"selections.{selection["index"]}.game_time": selection["game_time"]
                                    }}, 
                                return_document=ReturnDocument.AFTER
                            )
                            contestant_team_count = lineup_contestant['team_count']
                            if selection["player_id"] is not None: # new player and team to unavailables                
                                # if the team is already in the team count
                                if selection["team_abbreviation"] in contestant_team_count.keys():
                                    # if the team count has hit the limit
                                    if contestant_team_count[selection["team_abbreviation"]] + 1 == league_team_count:
                                        add_to_unavail_teams = await request.app.db["Contestants"].find_one_and_update(
                                            {"_id": lineup_contestant["_id"]},
                                            {"$push": 
                                                {
                                                    "unavailable_teams": {
                                                        "team_id": selection["team_id"],
                                                        "team_abbreviation": selection["team_abbreviation"]
                                                    }
                                                }
                                            }
                                        )
                                    # update the team count
                                    update_team_count = await request.app.db["Contestants"].find_one_and_update(
                                            {"_id": lineup_contestant["_id"]},
                                            {"$inc": 
                                                {
                                                    f"team_count.{selection["team_abbreviation"]}": 1
                                                }
                                            }
                                        )
                                else:
                                    update_team_count = await request.app.db["Contestants"].find_one_and_update(
                                            {"_id": lineup_contestant["_id"]},
                                            {"$inc": 
                                                {
                                                    f"team_count.{selection["team_abbreviation"]}": 1
                                                }
                                            }
                                        )

                                add_to_unavail_players = await request.app.db["Contestants"].find_one_and_update(
                                    {"_id": lineup_contestant["_id"]},
                                    {"$push": 
                                        {
                                            "unavailable_players": {
                                                "player_id": selection["player_id"],
                                                "player_name": selection["player_name"],
                                                "team_id": selection["team_id"],
                                                "team_abbreviation": selection["team_abbreviation"]
                                            }
                                        }
                                    }
                                )

                            if "player_id" in sel.keys(): # existing player and team removed from unavailables
                                
                                # if the team that's being removed is at the team count
                                if contestant_team_count[sel["team_abbreviation"]] == league_team_count:
                                    # remove from unavailable teams
                                    remove_from_unavail_teams = await request.app.db["Contestants"].find_one_and_update(
                                        {"_id": lineup_contestant["_id"]},
                                        {"$pull": 
                                            {
                                                "unavailable_teams": {
                                                    "team_id": sel["team_id"]
                                                }
                                            }
                                        }
                                    )      
                                    # update the team count
                                    update_team_count = await request.app.db["Contestants"].find_one_and_update(
                                            {"_id": lineup_contestant["_id"]},
                                            {"$inc": 
                                                {
                                                    f"team_count.{sel["team_abbreviation"]}": -1
                                                }
                                            }
                                        )
                                else:
                                    update_team_count = await request.app.db["Contestants"].find_one_and_update(
                                            {"_id": lineup_contestant["_id"]},
                                            {"$inc": 
                                                {
                                                    f"team_count.{sel["team_abbreviation"]}": -1
                                                }
                                            }
                                        )

                                remove_from_unavail_players = await request.app.db["Contestants"].find_one_and_update(
                                    {"_id": lineup_contestant["_id"]},
                                    {"$pull": 
                                        {
                                            "unavailable_players": {
                                                "player_id": sel["player_id"]
                                            }
                                        }
                                    }
                                )                           

                            return json.loads(json_util.dumps(updated_lineup))
                        else:
                            raise HTTPException(status_code=400, detail=f"This selection slot is locked")
            else:
                raise HTTPException(status_code=401, detail=f"Not authorized to edit Lineup {id}")
        else:
            raise HTTPException(status_code=404, detail=f"Lineup {id} not found")
        
        return json.loads(json_util.dumps(selection))

    # @router.delete("/lineup/{id}", response_description="Delete lineup")
    # async def delete_lineup(id: str, request: Request, user: User = Depends(current_active_user)):
    #     # Does contestant exist
    #     if (existing_contestant := await request.app.db["Contestants"].find_one({"_id": ObjectId(id)})) is not None:
    #         # Does the user id on the contestant match the user id of the requester
    #         if existing_contestant["user_id"] == user.id:
    #             # then delete the contestant
    #             delete_result = await request.app.db["Contestants"].delete_one({"_id": ObjectId(id)})

    #             # if the user/contestant is also the commissioner of the league
    #             #print(existing_contestant["league_id"])
    #             if (
    #                 con_is_commissh := await request.app.db["Leagues"].find_one(
    #                 {
    #                     "$and": [
    #                         {"_id": ObjectId(existing_contestant["league_id"])},
    #                         {"commissioner": ObjectId(user.id)}
    #                     ]
    #                 }
    #             )
    #             ) is not None:
    #                 print("here")
    #                 # Delete all contestants with the contestant ID
    #                 cursor = request.app.db["Contestants"].find({"league_id": ObjectId(existing_contestant["league_id"])})
    #                 for document in await cursor.to_list(length=100):
    #                     delete_contestants = await request.app.db["Contestants"].delete_one({"_id": document["_id"]})   
    #                 # and then delete the league
    #                 delete_league_result = await request.app.db["Leagues"].delete_one({"_id": ObjectId(existing_contestant["league_id"])})    

    #             if delete_result.deleted_count == 1:
    #                 return Response(status_code=status.HTTP_204_NO_CONTENT) 
            
    #         else:
    #             raise HTTPException(status_code=401, detail=f"Not authorized to delete contestant {id}")                           

    #     raise HTTPException(status_code=404, detail=f"contestant {id} not found")

    return router
