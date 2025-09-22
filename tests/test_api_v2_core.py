from http import HTTPStatus

from fastapi.testclient import TestClient


def test_health(anonymous_client: TestClient):
    result = anonymous_client.get("/api/v2/health/")
    assert result.status_code == HTTPStatus.OK
    resp_data = result.json()
    assert resp_data["data"]["code"] == 200
    assert resp_data["data"]["response_data"]["ok"]


def test_version(anonymous_client: TestClient):
    result = anonymous_client.get("/api/v2/version/")
    assert result.status_code == HTTPStatus.OK
    resp_data = result.json()
    for key in ["version", "build", "year", "url", "copyright", "client", "gateway"]:
        assert key in resp_data["data"]
