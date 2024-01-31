from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from beanie import PydanticObjectId

class ContestantModel(BaseModel):
    user_id: PydanticObjectId = Field(...)
    league_id: PydanticObjectId = Field(...)
    team_name: Optional[str] = Field(...)
    team_abbv: Optional[str] = Field(...)
    team_logo: Optional[str] = Field(...)
    locked: bool = Field(...)
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

class UpdateContestanteModel(BaseModel):
    team_name: Optional[str] = Field(...)
    team_abbv: Optional[str] = Field(...)
    team_logo: Optional[str] = Field(...)
    locked: bool = Field(...)
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
