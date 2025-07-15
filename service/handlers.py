from random import choice
from typing import Any
from uuid import UUID, uuid4

from fastapi import APIRouter, status

from api.v2.pools.schemas import PoolShortModel
from core.db import fake_pools_db
from core.enums import ConnectionTypes, EnitityStatuses, OSTypes, PoolTypes
from service.schemas import ExtendEmptyPoolRequestModel

service_router = APIRouter(tags=["service", "mock"], prefix="/service")


@service_router.get("/health")
async def health():
    return {"status": "ok"}


@service_router.get("/all-pools", status_code=status.HTTP_200_OK, response_model=list[PoolShortModel])
async def get_all_pools() -> list[PoolShortModel]:
    return [PoolShortModel(**pool) for pool in fake_pools_db.values()]


@service_router.post(
    "/extend-empty-pools", status_code=status.HTTP_201_CREATED, response_model=list[dict[str, dict[str, Any]]]
)
async def extend_empty_pools(request_model: ExtendEmptyPoolRequestModel) -> list[dict[str, dict[str, Any]]]:
    # TODO: привязка пула к пользователю - указать в ручке создания пулов
    # TODO: привязка ВМ к пулу - параметр в ручке создания пулов
    # TODO: переименовать ручку
    created_pools: list[dict[str, dict[str, Any]]] = []
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
        fake_pools_db.update(created_pool)
        created_pools.append(created_pool)
    return created_pools


# TODO: ручка списка пользователей (fake_users_db)
# TODO: ручка создания пользователя?
