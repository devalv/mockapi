from typing import Annotated

from pydantic import BaseModel, Field


class ExtendEmptyPoolRequestModel(BaseModel):
    count: Annotated[int, Field(ge=1, le=500)] = 1
