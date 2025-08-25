from typing import Annotated

from pydantic import UUID4, BaseModel, Field
from pydantic.networks import IPvAnyAddress

from api.v2.tasks.schemas import TaskShortModel
from core.enums import ConnectionTypes, EnitityStatuses, OSTypes, PermissionTypes, PoolTypes


class PoolShortModel(BaseModel):
    id: UUID4
    name: str
    status: EnitityStatuses
    is_favorite: bool
    pool_type: PoolTypes
    os_type: OSTypes = OSTypes.OTHER
    connection_types: list[ConnectionTypes]


class PoolShortResponseModel(BaseModel):
    data: PoolShortModel


class PoolGetMachineRequestModel(BaseModel):
    remote_protocol: ConnectionTypes
    width: Annotated[int, Field(ge=2)]
    height: Annotated[int, Field(ge=2)]
    password: str | None


class MachineShortResponseModel(BaseModel):
    id: UUID4
    verbose_name: str
    permissions: list[PermissionTypes]
    host: IPvAnyAddress
    vm_controller_address: IPvAnyAddress
    port: Annotated[int, Field(ge=1, le=65535)]
    status: EnitityStatuses


class PoolGetMachineResponseModel(BaseModel):
    data: MachineShortResponseModel


class PoolGetMachineActiveTaskResponseModel(BaseModel):
    data: TaskShortModel
