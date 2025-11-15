"""FastAPI application entry point"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy import text
from datetime import datetime

from app.config import settings
from app.database import init_db, engine
from app.api import stocks, prices, trading, news, refresh, chart
from app.utils.redis import test_redis_connection, close_redis_client
from app.exceptions import BaseAPIException
from app.schemas.response import ErrorResponse

app = FastAPI(
    title="K-SectorRadar API",
    description="Korean High-Growth Sector Analysis API",
    version="1.0.0",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 예외 핸들러 등록
@app.exception_handler(BaseAPIException)
async def base_api_exception_handler(request: Request, exc: BaseAPIException):
    """커스텀 API 예외 핸들러"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            success=False,
            error=exc.detail,
            error_code=exc.error_code,
            detail=exc.detail,
            timestamp=datetime.now(),
        ).model_dump(mode='json'),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """요청 검증 오류 핸들러"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            success=False,
            error="Validation error",
            error_code="VALIDATION_ERROR",
            detail=str(exc),
            timestamp=datetime.now(),
        ).model_dump(mode='json'),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """일반 예외 핸들러"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            success=False,
            error="Internal server error",
            error_code="INTERNAL_ERROR",
            detail=str(exc) if settings.ENVIRONMENT == "development" else None,
            timestamp=datetime.now(),
        ).model_dump(mode='json'),
    )


# 라우터 등록
app.include_router(stocks.router, prefix="/api/stocks", tags=["stocks"])
app.include_router(prices.router, prefix="/api/prices", tags=["prices"])
app.include_router(trading.router, prefix="/api/stocks", tags=["trading"])
app.include_router(news.router, prefix="/api/stocks", tags=["news"])
app.include_router(chart.router, prefix="/api/stocks", tags=["chart"])
app.include_router(refresh.router, tags=["refresh"])


@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행"""
    await init_db()
    # Redis 연결 테스트
    if test_redis_connection():
        print("✅ Redis 연결 성공")
    else:
        print("⚠️ Redis 연결 실패 (캐싱 기능이 제한될 수 있습니다)")


@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 실행"""
    close_redis_client()


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {"message": "K-SectorRadar API", "version": "1.0.0"}


@app.get("/api/health")
async def health():
    """
    Health Check 엔드포인트
    
    서버, 데이터베이스, Redis 연결 상태를 확인합니다.
    """
    # 데이터베이스 연결 상태 확인
    db_status = "disconnected"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            db_status = "connected"
    except Exception:
        db_status = "disconnected"
    
    # Redis 연결 상태 확인
    redis_status = "connected" if test_redis_connection() else "disconnected"
    
    # 전체 상태 결정
    overall_status = "healthy" if db_status == "connected" else "unhealthy"
    
    return {
        "status": overall_status,
        "database": db_status,
        "redis": redis_status,
        "timestamp": datetime.now().isoformat(),
    }

