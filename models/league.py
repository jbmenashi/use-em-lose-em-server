from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from beanie import PydanticObjectId

class Roster(BaseModel):
    roster_size: int = Field(...)
    positions: object = Field(...)

class Scoring(BaseModel):
    statistics: object = Field(...)

class LeagueModel(BaseModel):
    commissioner: Optional[PydanticObjectId] = None
    league_name: str = Field(...)
    sport: str = Field(...)
    year: int = Field(...)
    style: str = Field(...)
    number_of_players: int = Field(...)
    regular_season_weeks: int = Field(...)
    playoff_teams: int = Field(...)
    playoff_weeks: int = Field(...)
    team_parity: bool = Field(...)
    roster: Roster = Field(...)
    scoring: Scoring = Field(...)
    locked: bool = Field(...)
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "league_name": "Rotisserie Chicken",
                "sport": "Baseball",
                "style": "Points",
                "number_of_players": 12,
                "regular_season_weeks": 22,
                "playoff_teams": 6,
                "playoff_weeks": 3,
                "team_parity": True,
                "roster": {},
                "scoring": {}
            }
        },
    )



class UpdateLeagueModel(BaseModel):
    """
    A set of optional updates to be made to a document in the database.
    """

    league_name: Optional[str] = None
    style: Optional[str] = None
    number_of_players: Optional[int] = None
    regular_season_weeks: Optional[int] = None
    playoff_teams: Optional[int] = None
    playoff_weeks: Optional[int] = None
    team_parity: Optional[bool] = None
    roster: Optional[Roster] = None
    scoring: Optional[Scoring] = None
    locked: Optional[bool] = None
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={PydanticObjectId: str},
        json_schema_extra={
            "example": {
                "league_name": "Rotisserie Chicken",
                "sport": "Baseball",
                "style": "Points",
                "number_of_players": 12,
                "regular_season_weeks": 22,
                "playoff_teams": 6,
                "playoff_weeks": 3,
                "team_parity": True,
                "roster": {},
                "scoring": {}
            }
        },
    )
