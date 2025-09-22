"""Проверяем, что базовое поведение ручек не изменилось игнорируя контракт, т.к. это сервисная история."""

from http import HTTPStatus

from fastapi.testclient import TestClient


def test_get_all_tasks(anonymous_client: TestClient):
    result = anonymous_client.get("/service/all-tasks/")
    assert result.status_code == HTTPStatus.OK


def test_get_all_users(anonymous_client: TestClient):
    result = anonymous_client.get("/service/all-users/")
    assert result.status_code == HTTPStatus.OK


def test_get_all_pools(anonymous_client: TestClient):
    result = anonymous_client.get("/service/all-pools/")
    assert result.status_code == HTTPStatus.OK


def test_create_pools(anonymous_client: TestClient):
    initial_pools_count = len(anonymous_client.get("/service/all-pools/").json())
    result = anonymous_client.post(
        "/service/create-pools/",
        json={"count": 2, "assigned_users": ["516d600c-4273-40b8-8f5c-105cc3a4bbc9"], "create_machines_count": 1},
    )
    assert result.status_code == HTTPStatus.CREATED
    final_pools_count = len(anonymous_client.get("/service/all-pools/").json())
    assert final_pools_count == initial_pools_count + 2
