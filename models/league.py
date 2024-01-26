from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from beanie import PydanticObjectId


class LeagueModel(BaseModel):
    """
    Container for a single student record.
    """

    # The primary key for the StudentModel, stored as a `str` on the instance.
    # This will be aliased to `_id` when sent to MongoDB,
    # but provided as `id` in the API requests and responses.
    name: str = Field(...)
    course: str = Field(...)
    commissioner: Optional[PydanticObjectId] = None
    gpa: float = Field(..., le=4.0)
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "name": "Jane Doe",
                "course": "Experiments, Science, and Fashion in Nanophotonics",
                "gpa": 3.0,
            }
        },
    )



class UpdateLeagueModel(BaseModel):
    """
    A set of optional updates to be made to a document in the database.
    """

    name: Optional[str] = None
    course: Optional[str] = None
    gpa: Optional[float] = None
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={PydanticObjectId: str},
        json_schema_extra={
            "example": {
                "name": "Jane Doe",
                "course": "Experiments, Science, and Fashion in Nanophotonics",
                "gpa": 3.0,
            }
        },
    )
