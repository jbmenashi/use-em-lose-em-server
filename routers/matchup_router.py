from fastapi import APIRouter, Body, Request, HTTPException, status, Depends
from fastapi.responses import JSONResponse, Response

from auth.users import User, current_active_user
from models.matchup_model import MatchupModel
from pymongo import ReturnDocument
from beanie import PydanticObjectId

from bson import ObjectId, json_util
import json

def get_matchup_router(app):

    router = APIRouter()
    
    @router.get("/matchup/{id}", response_description="Get a single matchup", response_model=MatchupModel, response_model_by_alias=False)
    async def get_matchup(id: str, request: Request, user: User = Depends(current_active_user)):
        cursor = request.app.db["Matchups"].aggregate(
            [
                {
                    '$match': {
                        '_id': ObjectId(id)
                    }
                },
                {
                    '$lookup': {
                        'from': 'Lineups', 
                        'let': {
                            'matchup_team_1_id': '$team_1_id', 
                            'matchup_season': '$season', 
                            'matchup_week': '$week'
                        }, 
                        'pipeline': [
                            {
                                '$match': {
                                    '$expr': {
                                        '$and': [
                                            {
                                                '$eq': [
                                                    '$$matchup_team_1_id', '$contestant_id'
                                                ]
                                            }, {
                                                '$eq': [
                                                    '$$matchup_season', '$season'
                                                ]
                                            }, {
                                                '$eq': [
                                                    '$$matchup_week', '$week'
                                                ]
                                            }
                                        ]
                                    }
                                }
                            }
                        ], 
                        'as': 'team_1_lineup'
                    }
                },
                {
                    '$lookup': {
                        'from': 'Lineups', 
                        'let': {
                            'matchup_team_2_id': '$team_2_id', 
                            'matchup_season': '$season', 
                            'matchup_week': '$week'
                        }, 
                        'pipeline': [
                            {
                                '$match': {
                                    '$expr': {
                                        '$and': [
                                            {
                                                '$eq': [
                                                    '$$matchup_team_2_id', '$contestant_id'
                                                ]
                                            }, {
                                                '$eq': [
                                                    '$$matchup_season', '$season'
                                                ]
                                            }, {
                                                '$eq': [
                                                    '$$matchup_week', '$week'
                                                ]
                                            }
                                        ]
                                    }
                                }
                            }
                        ], 
                        'as': 'team_2_lineup'
                    }
                },
                {
                    '$project': {
                        '_id': 1,
                        'league_id': 1,
                        'season': 1,
                        'week': 1,
                        'season_type': 1,
                        'team_1_id': 1,
                        'team_1_name': 1,
                        'team_1_score': 1,
                        'team_1_lineup': {'$arrayElemAt': ['$team_1_lineup', 0]},
                        'team_2_id': 1,
                        'team_2_name': 1,
                        'team_2_score': 1,
                        'team_2_lineup': {'$arrayElemAt': ['$team_2_lineup', 0]},
                        'winner': 1,
                        'loser': 1,
                        'finished': 1,
                    }
                }
            ]
        )

        for matchup in await cursor.to_list(length=100):
            matchup = json.loads(json_util.dumps(matchup))
            transformedMatchup = {
                "_id": matchup["_id"]["$oid"],
                "league_id": matchup["league_id"]["$oid"],
                "season": matchup["season"],
                "week": matchup["week"],
                "season_type": matchup["season_type"],
                "team_1_id": matchup["team_1_id"]["$oid"],
                "team_1_name": matchup["team_1_name"],
                "team_1_score": matchup["team_1_score"],
                "team_1_lineup": matchup["team_1_lineup"],
                "team_2_id": matchup["team_2_id"]["$oid"],
                "team_2_name": matchup["team_2_name"],
                "team_2_score": matchup["team_2_score"],
                "team_2_lineup": matchup["team_2_lineup"],
                "winner": matchup["winner"],
                "loser": matchup["loser"],
                "finished": matchup["finished"],

            }
            transformedMatchup["team_1_lineup"]["_id"] = matchup["team_1_lineup"]["_id"]["$oid"]
            transformedMatchup["team_1_lineup"]["contestant_id"] = matchup["team_1_lineup"]["contestant_id"]["$oid"]
            transformedMatchup["team_1_lineup"]["league_id"] = matchup["team_1_lineup"]["league_id"]["$oid"]
            transformedMatchup["team_2_lineup"]["_id"] = matchup["team_2_lineup"]["_id"]["$oid"]
            transformedMatchup["team_2_lineup"]["contestant_id"] = matchup["team_2_lineup"]["contestant_id"]["$oid"]
            transformedMatchup["team_2_lineup"]["league_id"] = matchup["team_2_lineup"]["league_id"]["$oid"]
            return transformedMatchup
        
        raise HTTPException(status_code=404, detail=f"Matchup {id} not found")
    
    return router
