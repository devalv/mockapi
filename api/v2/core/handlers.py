from fastapi import APIRouter, status

from api.v2.core.schemas import HealthResponseModel, VersionResponseModel

v2_core_router = APIRouter()


@v2_core_router.get("/health/", status_code=status.HTTP_200_OK, response_model=HealthResponseModel)
async def health():
    return HealthResponseModel(
        data={
            "code": 200,
            "response_data": {"ok": True, "hostname": "2ec4a07b9dd4", "timestamp": 1753277200.0986974, "detail": ""},
        }
    )


@v2_core_router.get("/version/", status_code=status.HTTP_200_OK, response_model=VersionResponseModel)
async def version():
    return VersionResponseModel(
        data={
            "version": "7.0.1",
            "build": "996",
            "year": "2025-2026",
            "url": "https://spacevm.ru",
            "copyright": "spacevm.ru",
            "client": "4.0.0",
            "gateway": "2.0.0",
        }
    )
