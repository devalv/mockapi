from typing import Any
from uuid import UUID

fake_users_db: dict[str, dict[str, Any]] = {
    "johndoe": {
        "id": UUID("7e1459c2-3e19-4c3d-98f5-8344d44ae6f4").hex,
        "username": "johndoe",
        "disabled": False,
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "password": "Bazalt1!",
        "roles": ["admin", "user"],
    }
}


def get_user(db, username: str):
    if username in db:
        return db[username]
