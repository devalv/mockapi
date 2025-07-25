from typing import Annotated

from pydantic import BaseModel, Field

from api.v2.pools.schemas import MachineShortResponseModel, PoolShortModel
from core.schemas import User


class CreatePoolRequestModel(BaseModel):
    count: Annotated[int, Field(ge=1, le=500)] = 1
    create_machines_count: Annotated[int, Field(ge=1, le=500)] = 0
    assigned_users: list[str] = []


class CreatePoolResponseModel(PoolShortModel):
    pass


class ExtendedUserResponseModel(User):
    assigned_pools: list[PoolShortModel] = []
    assigned_machines: list[MachineShortResponseModel] = []
