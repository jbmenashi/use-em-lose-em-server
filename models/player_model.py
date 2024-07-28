from pydantic import BaseModel, Field

class SeasonStatsModel(BaseModel):
    stats: dict = {}

class ProjectionsModel(BaseModel):
    week: int = Field(...)
    stats: dict = {}

class PlayerModel(BaseModel):
    player_id: int = Field(...)
    player_name: str = Field(...)
    status: str = Field(...)
    team_id: int = Field(...)
    team_abbv: str = Field(...)
    jersey_num: int = Field(...)
    position_category: str = Field(...)
    position: str = Field(...)
    season_stats: SeasonStatsModel = Field(...)
    projections: ProjectionsModel = Field(...)