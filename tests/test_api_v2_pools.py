from datetime import datetime, timezone
from http import HTTPStatus
from time import sleep
from typing import Any
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from core.db import fake_machines_db, fake_tasks_db, fake_users_machines_db
from core.enums import ConnectionTypesMap, EnitityStatuses, TaskKinds, TaskStatuses


def test_get_pools(authenticated_client_user_2: TestClient):
    result = authenticated_client_user_2.get("/api/v2/pools/")
    assert result.status_code == HTTPStatus.OK
    assert result.json()["total"] == 2
    assert result.json()["page"] == 1
    assert result.json()["size"] == 50
    assert result.json()["pages"] == 1


def test_get_pools_favourite_only(authenticated_client_user_2: TestClient):
    result = authenticated_client_user_2.get("/api/v2/pools/", params={"is_favorite": True})
    assert result.status_code == HTTPStatus.OK
    assert result.json()["total"] == 1
    assert result.json()["page"] == 1
    assert result.json()["size"] == 50
    assert result.json()["pages"] == 1


def test_get_pools_anonymous(anonymous_client: TestClient):
    result = anonymous_client.get("/api/v2/pools/")
    assert result.status_code == HTTPStatus.FORBIDDEN


def test_pool_connect_stage1_anonymous(anonymous_client: TestClient):
    result = anonymous_client.get("/api/v2/pools/bc4f9e45-6b5a-41e6-bb85-ae91f4b8c413/connect/")
    assert result.status_code == HTTPStatus.FORBIDDEN


def test_pool_connect_stage1_blocked_expand(authenticated_client_user_2: TestClient):
    result = authenticated_client_user_2.get("/api/v2/pools/bc4f9e45-6b5a-41e6-bb85-ae91f4b8c413/connect/")
    assert result.status_code == HTTPStatus.FORBIDDEN
    assert result.json() == {"detail": [{"msg": "Pool cannot be expanded.", "err_code": 800, "type": "default"}]}


def test_pool_connect_stage1_astravdi(authenticated_client_astravdi: TestClient):
    result = authenticated_client_astravdi.get("/api/v2/pools/bc4f9e45-6b5a-41e6-bb85-ae91f4b8c413/connect/")
    # 202 код значит, что была создана задача на расширение
    assert result.status_code == HTTPStatus.ACCEPTED
    sleep(0.1)
    assert result.json()["data"]["id"] in fake_tasks_db["7e1459c2-3e19-4c3d-98f5-8344d44ae6f4"]
    assert result.json()["data"]["kind"] == "POOL_EXPAND"


def test_pool_connect_stage2_anonymous(anonymous_client: TestClient):
    result = anonymous_client.post("/api/v2/pools/bc4f9e45-6b5a-41e6-bb85-ae91f4b8c413/connect/")
    assert result.status_code == HTTPStatus.FORBIDDEN


def test_pool_connect_stage2_astravdi_without_stage1(authenticated_client_astravdi: TestClient):
    result = authenticated_client_astravdi.post(
        "/api/v2/pools/bc4f9e45-6b5a-41e6-bb85-ae91f4b8c413/connect/",
        json={"password": "test", "remote_protocol": 1, "width": 2, "height": 2},
    )
    assert result.status_code == HTTPStatus.CONFLICT


@pytest.fixture
def task_stage_1():
    fake_user_id: str = "7e1459c2-3e19-4c3d-98f5-8344d44ae6f4"
    if fake_user_id not in fake_tasks_db:
        fake_tasks_db[fake_user_id] = dict()
    fake_task_id: str = f"{uuid4()}"
    fake_tasks_db[fake_user_id][fake_task_id] = {
        "status": TaskStatuses.COMPLETED,
        "created": datetime.now(timezone.utc),
        "started": datetime.now(timezone.utc),
        "finished": datetime.now(timezone.utc),
        "id": fake_task_id,
        "kind": TaskKinds.POOL_EXPAND,
    }
    new_machine_id: UUID = uuid4()
    new_machine: dict[str, Any] = {
        "id": new_machine_id.hex,
        "verbose_name": f"machine-{new_machine_id.hex[:4]}",
        "status": EnitityStatuses.ACTIVE,
        "pool_id": "bc4f9e45-6b5a-41e6-bb85-ae91f4b8c413",
        "address": "127.0.0.1",
        "permissions": [],
        "host": "127.0.0.1",
        "port": 3398,
        "protocol_id": ConnectionTypesMap.GLINTV1,
    }
    fake_machines_db[f"{new_machine_id}"] = new_machine
    if not fake_machines_db.get(fake_user_id):
        fake_users_machines_db[fake_user_id] = set()
    fake_users_machines_db[fake_user_id].add(f"{new_machine_id}")
    yield
    fake_tasks_db["7e1459c2-3e19-4c3d-98f5-8344d44ae6f4"].pop(fake_task_id)


def test_pool_connect_stage2_astravdi(authenticated_client_astravdi: TestClient, task_stage_1):
    result = authenticated_client_astravdi.post(
        "/api/v2/pools/bc4f9e45-6b5a-41e6-bb85-ae91f4b8c413/connect/",
        json={"password": "test", "remote_protocol": 1, "width": 2, "height": 2},
    )
    assert result.status_code == HTTPStatus.ACCEPTED
    sleep(0.1)
    assert result.json()["data"]["id"] in fake_tasks_db["7e1459c2-3e19-4c3d-98f5-8344d44ae6f4"]
    assert result.json()["data"]["kind"] == "GLINT_START"
