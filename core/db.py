from typing import Any
from uuid import UUID

fake_users_db: dict[str, dict[str, Any]] = {
    "astravdi": {
        "id": UUID("7e1459c2-3e19-4c3d-98f5-8344d44ae6f4").hex,
        "username": "astravdi",
        "disabled": False,
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "password": "Bazalt1!",
        "roles": ["admin", "user"],
    },
    "user-1": {
        "id": UUID("516d600c-4273-40b8-8f5c-105cc3a4bbc9").hex,
        "username": "user-1",
        "disabled": True,
        "full_name": "Yoba Pekas",
        "email": "yobap@example.com",
        "password": "Bazalt1!",
        "roles": ["user"],
    },
    "user-2": {
        "id": UUID("e8d8dd14-cb09-4099-b96e-a83c6b09496c").hex,
        "username": "user-2",
        "disabled": False,
        "full_name": "Lupis Pupas",
        "email": "lupisp@example.com",
        "password": "Bazalt1!",
        "roles": ["user"],
    },
}


fake_pools_db: dict[str, dict[str, Any]] = {
    "bc4f9e45-6b5a-41e6-bb85-ae91f4b8c413": {
        "id": UUID("bc4f9e45-6b5a-41e6-bb85-ae91f4b8c413").hex,
        "name": "pool-win-1",
        "status": "ACTIVE",
        "is_favorite": True,
        "pool_type": "AUTOMATED",
        "os_type": "Windows",
        "connection_types": ["RDP", "NATIVE_RDP"],
    },
    "22aaa425-6387-4767-9611-3c26ad1a6161": {
        "id": UUID("22aaa425-6387-4767-9611-3c26ad1a6161").hex,
        "name": "pool-win-2",
        "status": "ACTIVE",
        "is_favorite": False,
        "pool_type": "AUTOMATED",
        "os_type": "Windows",
        "connection_types": ["RDP", "NATIVE_RDP"],
    },
    "35f4392a-2cc6-4f9b-aea5-dce568493175": {
        "id": UUID("35f4392a-2cc6-4f9b-aea5-dce568493175").hex,
        "name": "pool-astra-1",
        "status": "ACTIVE",
        "is_favorite": False,
        "pool_type": "STATIC",
        "os_type": "Linux",
        "connection_types": ["GLINT"],
    },
    "2378c527-64eb-48cf-817a-645b645dba54": {
        "id": UUID("2378c527-64eb-48cf-817a-645b645dba54").hex,
        "name": "pool-astra-2",
        "status": "ACTIVE",
        "is_favorite": False,
        "pool_type": "STATIC",
        "os_type": "Linux",
        "connection_types": ["GLINT"],
    },
}


fake_users_pools_db: dict[str, set[str]] = {
    "7e1459c2-3e19-4c3d-98f5-8344d44ae6f4": set([
        "bc4f9e45-6b5a-41e6-bb85-ae91f4b8c413",
        "22aaa425-6387-4767-9611-3c26ad1a6161",
        "35f4392a-2cc6-4f9b-aea5-dce568493175",
        "2378c527-64eb-48cf-817a-645b645dba54",
    ]),
    "516d600c-4273-40b8-8f5c-105cc3a4bbc9": set(),
    "e8d8dd14-cb09-4099-b96e-a83c6b09496c": set([
        "bc4f9e45-6b5a-41e6-bb85-ae91f4b8c413",
        "2378c527-64eb-48cf-817a-645b645dba54",
    ]),
}


def get_user(username: str):
    if username in fake_users_db:
        return fake_users_db[username]


def get_user_pools(user_id: str) -> list[dict[str, Any]]:
    if user_id in fake_users_pools_db:
        pool_ids = fake_users_pools_db[user_id]
        pools: list[dict[str, Any]] = []
        for pool in pool_ids:
            pools.append(fake_pools_db[pool])
        return pools
    return []
