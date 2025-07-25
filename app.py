from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi_pagination import add_pagination

from api.v2 import v2_core_router, v2_pools_router, v2_users_router
from core.errors import ErrorCodes
from service.handlers import service_router

mock_app = FastAPI()
mock_app.include_router(v2_pools_router, prefix="/api/v2", tags=["v2"])
mock_app.include_router(v2_users_router, prefix="/api/v2", tags=["v2"])
mock_app.include_router(v2_core_router, prefix="/api/v2", tags=["v2"])
mock_app.include_router(service_router, prefix="", tags=["service", "mock"])
add_pagination(mock_app)


@mock_app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    _errors: list[dict[str, Any]] | Any = exc.errors()
    if _errors and isinstance(_errors, list):
        for _err in _errors:
            if _err and isinstance(_err, dict) and "err_code" not in _err:
                _err["err_code"] = ErrorCodes.UNKNOWN

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        # content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),  # debug option?  # noqa E501
        content=jsonable_encoder({"detail": exc.errors()}),
    )
