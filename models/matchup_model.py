from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from beanie import PydanticObjectId
from models.lineup_model import LineupModel
from bson import ObjectId

class MatchupModel(BaseModel):
    league_id: PydanticObjectId = Field(...)
    season: int = Field(...)
    week: int = Field(...)
    season_type: str = Field(...)
    team_1_id: PydanticObjectId = Field(...)
    team_1_name: str = Field(...)
    team_1_score: float = Field(...)
    team_1_lineup: LineupModel = Field(...)
    team_2_id: PydanticObjectId = Field(...)
    team_2_name: str = Field(...)
    team_2_score: float = Field(...)
    team_2_lineup: LineupModel = Field(...)
    winner: Optional[PydanticObjectId] = None
    loser: Optional[PydanticObjectId] = None
    finished: bool = Field(...)
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "sport": "MLB",
                "style": "Rotisserie",
                "week": 1,
                "outcome": {},
                "selections": [],
                "locked": False
            }
        },
    )
