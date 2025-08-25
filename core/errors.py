from typing import Any, Dict

from fastapi import HTTPException, status

from core.enums import ErrorCodes
from core.schemas import DetailContent


class MockApiHTTPError(HTTPException):
    def __init__(self, status_code: int, detail: Any = None, headers: Dict[str, str] | None = None) -> None:
        super().__init__(status_code, detail, headers)


CREDENTIALS_ERR: MockApiHTTPError = MockApiHTTPError(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail=[DetailContent(msg="Invalid Credentials.", err_code=ErrorCodes.UNKNOWN).model_dump()],
    headers={"WWW-Authenticate": "JWT"},
)

FORBIDEN_ERR: MockApiHTTPError = MockApiHTTPError(
    status_code=status.HTTP_403_FORBIDDEN,
    detail=[DetailContent(msg="Permission denied.", err_code=ErrorCodes.UNKNOWN).model_dump()],
    headers={"WWW-Authenticate": "JWT"},
)

TOKEN_TYPE_ERR: MockApiHTTPError = MockApiHTTPError(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    detail=[DetailContent(msg="Invalid token type.", err_code=ErrorCodes.UNKNOWN).model_dump()],
    headers={"WWW-Authenticate": "JWT"},
)

NOT_FOUND_ERR: MockApiHTTPError = MockApiHTTPError(
    status_code=status.HTTP_404_NOT_FOUND,
    detail=[DetailContent(msg="Not found.", err_code=ErrorCodes.UNKNOWN).model_dump()],
    headers={"WWW-Authenticate": "JWT"},
)

POOL_EXPAND_FAILED_ERR: MockApiHTTPError = MockApiHTTPError(
    status_code=status.HTTP_403_FORBIDDEN,
    detail=[DetailContent(msg="Not found.", err_code=ErrorCodes.POOL_EXPAND_FAILED).model_dump()],
    headers={"WWW-Authenticate": "JWT"},
)
