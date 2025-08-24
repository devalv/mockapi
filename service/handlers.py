from random import choice
from typing import Any
from uuid import UUID, uuid4

from fastapi import APIRouter, status

from api.v2.pools.schemas import MachineShortResponseModel, PoolShortModel
from core.db import (
    fake_machines_db,
    fake_pools_db,
    fake_users_db,
    fake_users_pools_db,
    get_user_machines,
    get_user_pools,
)
from core.enums import ConnectionTypes, EnitityStatuses, OSTypes, PoolTypes
from service.schemas import CreatePoolRequestModel, CreatePoolResponseModel, ExtendedUserResponseModel

service_router = APIRouter(tags=["service", "mock"], prefix="/service")


@service_router.get("/all-pools", status_code=status.HTTP_200_OK, response_model=list[PoolShortModel])
async def get_all_pools() -> list[PoolShortModel]:
    return [PoolShortModel(**pool) for pool in fake_pools_db.values()]


@service_router.post("/create-pools", status_code=status.HTTP_201_CREATED, response_model=list[CreatePoolResponseModel])
async def create_pools(request_model: CreatePoolRequestModel) -> list[CreatePoolResponseModel]:
    created_pools: list[CreatePoolResponseModel] = []
    for _ in range(request_model.count):
        new_pool_id: UUID = uuid4()
        new_pool: dict[str, Any] = {
            "id": new_pool_id.hex,
            "name": f"pool-{new_pool_id.hex[:4]}",
            "status": choice(EnitityStatuses.values()),
            "is_favorite": choice((True, False)),
            "pool_type": choice(PoolTypes.values()),
            "os_type": choice(OSTypes.values()),
            "connection_types": [choice(ConnectionTypes.values())],
        }
        created_pool: dict[str, dict[str, Any]] = {new_pool_id.hex: new_pool}
        created_pools.append(CreatePoolResponseModel(**new_pool))
        fake_pools_db.update(created_pool)
        for user_id in request_model.assigned_users:
            fake_users_pools_db[user_id].add(new_pool_id.hex)
        for _ in range(request_model.create_machines_count):
            new_machine_id: UUID = uuid4()
            new_machine: dict[str, Any] = {
                "id": new_machine_id.hex,
                "name": f"machine-{new_machine_id.hex[:4]}",
                "status": EnitityStatuses.ACTIVE,
                "pool_id": f"{new_pool_id}",
                "address": "127.0.0.1",
            }
            fake_machines_db[f"{new_machine_id}"] = new_machine
    return created_pools


@service_router.get("/all-users", status_code=status.HTTP_200_OK, response_model=list[ExtendedUserResponseModel])
async def get_all_users() -> list[ExtendedUserResponseModel]:
    response_data: list[ExtendedUserResponseModel] = list()
    for user in fake_users_db.values():
        user_schema_obj: ExtendedUserResponseModel = ExtendedUserResponseModel(**user)
        user_schema_obj.assigned_pools = [PoolShortModel(**pool) for pool in get_user_pools(str(UUID(user["id"])))]
        user_schema_obj.assigned_machines = [
            MachineShortResponseModel(**machine) for machine in get_user_machines(str(UUID(user["id"])))
        ]
        response_data.append(user_schema_obj)
    return response_data


# TODO: tasks list
