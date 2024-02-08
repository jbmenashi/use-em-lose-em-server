from pydantic import BaseModel, Field

class StandingsContestantModel(BaseModel):
    rank: int = Field(...)
    criteria: dict = {}

class StandingsModel(BaseModel):
    league_id: int = Field(...)
    sport: str = Field(...)
    style: str = Field(...)
    contestants: list[StandingsContestantModel] = Field(...)