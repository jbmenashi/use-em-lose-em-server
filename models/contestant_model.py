from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from beanie import PydanticObjectId

class ContestantModel(BaseModel):
    user_id: Optional[PydanticObjectId] = None
    league_id: Optional[PydanticObjectId] = None
    team_name: Optional[str] = None
    team_abbv: Optional[str] = None
    team_logo: Optional[str] = None
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
    team_name: Optional[str] = None
    team_abbv: Optional[str] = None
    team_logo: Optional[str] = None
    locked: Optional[bool] = None
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
