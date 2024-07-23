from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from beanie import PydanticObjectId


# class GameLog(BaseModel):
#     game_date: str = Field(...)
#     stats: dict = Field(...)

# class TotalStats(BaseModel):
#     stats: dict = Field(...)

class Selection(BaseModel):
    player_id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    team_id: Optional[int] = None
    team_abbreviation: Optional[str] = None
    position: str = Field(...)
    fantasy_stats: Optional[dict] = None
    total_points: float = 0
    locked: bool = False
    index: Optional[int] = None

class LineupModel(BaseModel):
    contestant_id: Optional[PydanticObjectId] = None
    league_id: Optional[PydanticObjectId] = None
    sport: str = Field(...)
    style: str = Field(...)
    season: int = Field(...)
    week: int = Field(...)
    selections: list[Selection] = Field(...)
    score: float = 0
    locked: bool = False
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

class UpdateLineupModel(BaseModel):
    selection: Optional[Selection] = None
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "selection": {},
                "locked": False
            }
        },
    )
