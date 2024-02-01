from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from beanie import PydanticObjectId

class Roster(BaseModel):
    roster_size: int = Field(...)
    positions: dict = {}

class Scoring(BaseModel):
    statistics: dict = {}

class LeagueModel(BaseModel):
    commissioner: Optional[PydanticObjectId] = None
    league_name: str = Field(...)
    sport: str = Field(...)
    season: int = Field(...)
    style: str = Field(...)
    size: int = Field(...)
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
                "season": 2024,
                "style": "Points",
                "size": 12,
                "regular_season_weeks": 22,
                "playoff_teams": 6,
                "playoff_weeks": 3,
                "team_parity": True,
                "roster": {
                    "roster_size": 6,
                    "positions": {}
                },
                "scoring": {
                    "statistics": {}
                },
                "locked": False
            }
        },
    )



class UpdateLeagueModel(BaseModel):
    """
    A set of optional updates to be made to a document in the database.
    """

    league_name: Optional[str] = None
    style: Optional[str] = None
    size: Optional[int] = None
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
                "roster": {
                    "roster_size": 6,
                    "positions": {}
                },
                "scoring": {
                    "statistics": {}
                },
            }
        },
    )
