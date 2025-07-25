from pydantic import BaseModel


class ResponseDataDataModel(BaseModel):
    ok: bool
    hostname: str
    timestamp: float
    detail: str


class HealthResponseDataModel(BaseModel):
    code: int
    response_data: ResponseDataDataModel


class HealthResponseModel(BaseModel):
    data: HealthResponseDataModel

    class Config:
        schema_extra = {
            "example": {
                "data": {
                    "code": 200,
                    "response_data": {
                        "ok": True,
                        "hostname": "2ec4a07b9dd4",
                        "timestamp": 1753277200.0986974,
                        "detail": "",
                    },
                }
            }
        }


class VersionDataModel(BaseModel):
    version: str
    build: str
    year: str
    url: str
    copyright: str
    client: str
    gateway: str


class VersionResponseModel(BaseModel):
    data: VersionDataModel

    class Config:
        schema_extra = {
            "example": {
                "data": {
                    "version": "7.0.0",
                    "build": "996",
                    "year": "2025-2026",
                    "url": "https://spacevm.ru",
                    "copyright": "spacevm.ru",
                    "client": "4.0.0",
                    "gateway": "2.0.0",
                }
            }
        }
