from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from app import mock_app
from core.schemas import TokenData, User
from core.utils import authenticate_user_with_password


@pytest.fixture
def anonymous_client():
    with TestClient(app=mock_app) as ac:
        yield ac


@pytest.fixture
def token_data_user_2() -> TokenData:
    _u: User | None = authenticate_user_with_password(username="user-2", password="test")
    assert _u
    return TokenData(
        username=_u.username,
        sub=_u.id,
        roles=_u.roles,
        domain=None,
        exp=(datetime.now(timezone.utc) + timedelta(hours=24)).timestamp(),
        client_id=f"{_u.id}",
    )


@pytest.fixture
def token_data_astravdi() -> TokenData:
    _u: User | None = authenticate_user_with_password(username="astravdi", password="test")
    assert _u
    return TokenData(
        username=_u.username,
        sub=_u.id,
        roles=_u.roles,
        domain=None,
        exp=(datetime.now(timezone.utc) + timedelta(hours=24)).timestamp(),
        client_id=f"{_u.id}",
    )


@pytest.fixture
def authenticated_client_user_2(token_data_user_2):
    with TestClient(app=mock_app, headers={"Authorization": f"JWT {token_data_user_2.encode()}"}) as ac:
        yield ac


@pytest.fixture
def authenticated_client_astravdi(token_data_astravdi):
    with TestClient(app=mock_app, headers={"Authorization": f"JWT {token_data_astravdi.encode()}"}) as ac:
        yield ac
