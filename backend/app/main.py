"""FastAPI application entry point"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.api import stocks, prices, trading, news, refresh, chart

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

# 라우터 등록
app.include_router(stocks.router, prefix="/api/stocks", tags=["stocks"])
app.include_router(prices.router, prefix="/api/stocks", tags=["prices"])
app.include_router(trading.router, prefix="/api/stocks", tags=["trading"])
app.include_router(news.router, prefix="/api/stocks", tags=["news"])
app.include_router(chart.router, prefix="/api/stocks", tags=["chart"])
app.include_router(refresh.router, tags=["refresh"])


@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행"""
    await init_db()


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {"message": "K-SectorRadar API", "version": "1.0.0"}


@app.get("/health")
async def health():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy"}

