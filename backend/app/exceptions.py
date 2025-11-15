"""커스텀 예외 클래스 정의"""

from fastapi import HTTPException, status


class BaseAPIException(HTTPException):
    """기본 API 예외 클래스"""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str = None,
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code


class NotFoundException(BaseAPIException):
    """리소스를 찾을 수 없을 때 발생하는 예외"""
    
    def __init__(self, detail: str = "Resource not found", error_code: str = "NOT_FOUND"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code=error_code,
        )


class BadRequestException(BaseAPIException):
    """잘못된 요청일 때 발생하는 예외"""
    
    def __init__(self, detail: str = "Bad request", error_code: str = "BAD_REQUEST"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code=error_code,
        )


class InternalServerException(BaseAPIException):
    """서버 내부 오류일 때 발생하는 예외"""
    
    def __init__(self, detail: str = "Internal server error", error_code: str = "INTERNAL_ERROR"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code=error_code,
        )


class DatabaseException(BaseAPIException):
    """데이터베이스 오류일 때 발생하는 예외"""
    
    def __init__(self, detail: str = "Database error", error_code: str = "DATABASE_ERROR"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code=error_code,
        )

