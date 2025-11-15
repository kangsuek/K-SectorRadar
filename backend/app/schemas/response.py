"""공통 응답 스키마"""

from typing import Any, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class APIResponse(BaseModel):
    """공통 API 응답 스키마"""

    success: bool
    data: Any
    message: str = ""
    timestamp: Optional[datetime] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "data": {},
                "message": "",
                "timestamp": "2025-01-01T00:00:00Z"
            }
        }
    )


class ErrorResponse(BaseModel):
    """에러 응답 스키마"""

    success: bool = False
    error: str
    error_code: Optional[str] = None
    detail: Optional[str] = None
    timestamp: Optional[datetime] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": False,
                "error": "Resource not found",
                "error_code": "NOT_FOUND",
                "detail": "Stock with ticker '123456' not found",
                "timestamp": "2025-01-01T00:00:00Z"
            }
        }
    )

