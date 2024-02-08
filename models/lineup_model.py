from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from beanie import PydanticObjectId

class Selection(BaseModel):
    player_game_log_id: Optional[PydanticObjectId] = None
    player_id: int = Field(...)
    player_first_name: str = Field(...)
    player_last_name: str = Field(...)
    player_team_id: int = Field(...)
    player_position: str = Field(...)

class LineupModel(BaseModel):
    contestant_id: Optional[PydanticObjectId] = None
    league_id: Optional[PydanticObjectId] = None
    sport: str = Field(...)
    style: str = Field(...)
    week: int = Field(...)
    selections: list[Selection] = Field(...)
    outcome: dict = Field(...)
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
    selections: Optional[list[Selection]] = None
    locked: Optional[bool] = None
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "selections": [],
                "locked": False
            }
        },
    )
