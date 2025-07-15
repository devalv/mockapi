from pydantic import UUID4, BaseModel

from core.enums import ConnectionTypes, EnitityStatuses, OSTypes, PoolTypes


class PoolShortModel(BaseModel):
    id: UUID4
    name: str
    status: EnitityStatuses
    is_favorite: bool  # TODO: убрать из ответа?
    pool_type: PoolTypes
    os_type: OSTypes = OSTypes.OTHER
    connection_types: list[ConnectionTypes]


class PoolShortResponseModel(BaseModel):
    data: PoolShortModel
