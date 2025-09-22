from http import HTTPStatus

from fastapi.testclient import TestClient


def test_get_task(authenticated_client_user_2: TestClient):
    result = authenticated_client_user_2.get("/api/v2/tasks/22aaa425-6387-4767-9611-3c26ad1a6161/")
    assert result.status_code == HTTPStatus.OK


def test_get_another_user_task(authenticated_client_user_2: TestClient):
    result = authenticated_client_user_2.get("/api/v2/tasks/fabb9a84-ae96-4d07-b5a0-329ea70fa476/")
    assert result.status_code == HTTPStatus.NOT_FOUND


def test_get_task_is_done(authenticated_client_user_2: TestClient):
    result = authenticated_client_user_2.get("/api/v2/tasks/22aaa425-6387-4767-9611-3c26ad1a6161/is-done/")
    assert result.status_code == HTTPStatus.OK
    assert result.json()["data"]["is_done"] is True


def test_get_another_user_task_is_done(authenticated_client_user_2: TestClient):
    result = authenticated_client_user_2.get("/api/v2/tasks/fabb9a84-ae96-4d07-b5a0-329ea70fa476/is-done/")
    assert result.status_code == HTTPStatus.NOT_FOUND
