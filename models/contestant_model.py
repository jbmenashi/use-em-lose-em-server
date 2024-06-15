from typing import Optional
from pydantic import BaseModel, ConfigDict
from beanie import PydanticObjectId

class UnavailPlayer(BaseModel):
    player_id: int
    player_first_name: str
    player_last_name: str
    team_id: int 
    team_abbv: str

class UnavailTeam(BaseModel):
    team_id: int 
    team_abbv: str

class ContestantModel(BaseModel):
    user_id: Optional[PydanticObjectId] = None
    league_id: Optional[PydanticObjectId] = None
    team_name: Optional[str] = ""
    unavailable_players: Optional[list[UnavailPlayer]] = []
    unavailable_teams: Optional[list[UnavailTeam]] = []
    team_count: Optional[dict] = {}
    locked: Optional[bool] = None
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "team_name": "Jake's Team",
                "team_abbv": "JBM",
                "team_logo": "example.jpg"
            }
        },
    )

class UpdateContestantModel(BaseModel):
    team_name: Optional[str] = ""
    locked: Optional[bool] = None
    unavailable_players: Optional[list[UnavailPlayer]] = []
    unavailable_teams: Optional[list[UnavailTeam]] = []
    team_count: Optional[dict] = {}
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={PydanticObjectId: str},
        json_schema_extra={
            "example": {
                "team_name": "Jake's Team",
                "team_abbv": "JBM",
                "team_logo": "example.jpg"
            }
        },
    )
