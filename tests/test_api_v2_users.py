from datetime import datetime
from http import HTTPStatus

from fastapi.testclient import TestClient


def test_logout(authenticated_client_user_2: TestClient):
    result = authenticated_client_user_2.post("/api/v2/users/logout/")
    assert result.status_code == HTTPStatus.RESET_CONTENT


def test_logout_anonymous(anonymous_client: TestClient):
    result = anonymous_client.post("/api/v2/users/logout/")
    assert result.status_code == HTTPStatus.FORBIDDEN


def test_settings(authenticated_client_user_2: TestClient):
    result = authenticated_client_user_2.get("/api/v2/users/settings/")
    assert result.status_code == HTTPStatus.OK
    assert result.json() == {
        "data": {
            "general": {
                "admin_mode_enabled": False,
                "file_logging_enabled": False,
                "default_remote_protocol": 1,
                "last_pool_autoconnect_enabled": False,
                "automatically_install_updates_enabled": True,
                "documentation_url": "https://spacevm.ru/client-docs/latest/",
            },
            "security": {
                "otp_enabled": False,
                "adfs_enabled": False,
                "hardware_token_enabled": False,
                "domain_username_format_enabled": False,
                "sc_permissions": [],
            },
            "net": {"network_timeout": 15, "ws_channels": [{"channel": "api/v2/pools/ws/", "event": "pool_update"}]},
            "protocols": [
                {
                    "id": 1,
                    "name": "GLINT",
                    "version": "1.0.0",
                    "image_format": "BGRX32",
                    "fps": 30,
                    "keep_session_enabled": False,
                    "full_screen_enabled": True,
                    "multi_screen_enabled": False,
                    "scale_image_enabled": True,
                    "full_image_redraw_enabled": False,
                    "hardware_acceleration_options": {
                        "hardware_acceleration_enabled": False,
                        "video_compression_codec": "AVC420",
                        "h264_bitrate_mbs": 3,
                    },
                    "audio_playback_mode": "CLIENT",
                }
            ],
        }
    }


def test_settings_anonymous(anonymous_client: TestClient):
    result = anonymous_client.get("/api/v2/users/settings/")
    assert result.status_code == HTTPStatus.FORBIDDEN


def test_login_bad(anonymous_client: TestClient):
    result = anonymous_client.post("/api/v2/users/login/", json={"username": "test", "password": "test", "ldap": False})
    assert result.status_code == HTTPStatus.UNAUTHORIZED


def test_login_without_otp(anonymous_client: TestClient):
    result = anonymous_client.post(
        "/api/v2/users/login/", json={"username": "astravdi", "password": "test", "ldap": False}
    )
    assert result.status_code == HTTPStatus.OK
    resp_data: dict[str, dict[str, str]] = result.json()
    assert "data" in resp_data
    assert "access_token" in resp_data["data"]
    assert "refresh_token" in resp_data["data"]
    assert "token_type" in resp_data["data"]


def test_login_with_otp_enabled(anonymous_client: TestClient):
    result = anonymous_client.post(
        "/api/v2/users/login/", json={"username": "user-1", "password": "test", "ldap": False}
    )
    assert result.status_code == HTTPStatus.PRECONDITION_REQUIRED
    assert result.json() == {
        "detail": [{"msg": "MFA required.", "err_code": 100, "type": "auth", "next_step": "/api/v2/users/login/"}]
    }


def test_login_with_bad_otp_value(anonymous_client: TestClient):
    result = anonymous_client.post(
        "/api/v2/users/login/", json={"username": "user-1", "password": "test", "ldap": False, "otp_code": "123456"}
    )
    assert result.status_code == HTTPStatus.UNAUTHORIZED


def test_login_with_good_otp_value(anonymous_client: TestClient):
    result = anonymous_client.post(
        "/api/v2/users/login/",
        json={
            "username": "user-1",
            "password": "test",
            "ldap": False,
            "otp_code": f"{datetime.now().strftime("%y%m%d"):}",
        },
    )
    assert result.status_code == HTTPStatus.UNAUTHORIZED


def test_login_with_adfs_enabled(anonymous_client: TestClient):
    result = anonymous_client.post(
        "/api/v2/users/login/", json={"username": "user-5", "password": "test", "ldap": False}
    )
    assert result.status_code == HTTPStatus.PRECONDITION_REQUIRED
    assert result.json() == {
        "detail": [{"msg": "MFA required.", "err_code": 101, "type": "auth", "next_step": "/api/v2/users/adfs/"}]
    }


def test_login_with_hardware_token_enabled(anonymous_client: TestClient):
    result = anonymous_client.post(
        "/api/v2/users/login/", json={"username": "user-3", "password": "test", "ldap": False}
    )
    assert result.status_code == HTTPStatus.PRECONDITION_REQUIRED
    assert result.json() == {
        "detail": [
            {"msg": "MFA required.", "err_code": 102, "type": "auth", "next_step": "/api/v2/users/hardware_token/"}
        ]
    }
