"""주식 정보 API 라우터"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models.stock import Stock
from app.schemas.stock import StockResponse, StockListResponse
from app.schemas.response import APIResponse
from app.exceptions import NotFoundException
from app.utils.cache import get_cache, set_cache

router = APIRouter()

# 캐시 TTL (초)
CACHE_TTL = 3600  # 1시간


def _get_stocks_cache_key(type: Optional[str], theme: Optional[str], limit: int, offset: int) -> str:
    """종목 목록 캐시 키 생성"""
    key_parts = ["stocks:list"]
    if type:
        key_parts.append(f"type:{type}")
    if theme:
        key_parts.append(f"theme:{theme}")
    key_parts.append(f"limit:{limit}")
    key_parts.append(f"offset:{offset}")
    return ":".join(key_parts)


def _get_stock_cache_key(ticker: str) -> str:
    """종목 상세 캐시 키 생성"""
    return f"stocks:detail:{ticker}"


@router.get("", response_model=APIResponse)
async def get_stocks(
    type: Optional[str] = None,
    theme: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """
    전체 종목 목록 조회
    
    - **type**: 종목 유형 필터링 (STOCK/ETF)
    - **theme**: 테마 분류 필터링
    - **limit**: 페이지 크기 (기본값: 100)
    - **offset**: 오프셋 (기본값: 0)
    """
    # 캐시 키 생성
    cache_key = _get_stocks_cache_key(type, theme, limit, offset)
    
    # 캐시에서 조회 시도
    cached_data = get_cache(cache_key)
    if cached_data is not None:
        return APIResponse(
            success=True,
            data=cached_data,
            message="",
            timestamp=datetime.now(),
        )
    
    # 데이터베이스에서 조회
    query = db.query(Stock)

    if type:
        query = query.filter(Stock.type == type)
    if theme:
        query = query.filter(Stock.theme == theme)

    total = query.count()
    stocks = query.offset(offset).limit(limit).all()
    
    # 스키마로 변환
    stock_list = StockListResponse(
        stocks=[StockResponse.model_validate(stock) for stock in stocks],
        total=total,
        limit=limit,
        offset=offset,
    )
    
    # 캐시에 저장
    set_cache(cache_key, stock_list.model_dump(), CACHE_TTL)

    return APIResponse(
        success=True,
        data=stock_list.model_dump(),
        message="",
        timestamp=datetime.now(),
    )


@router.get("/{ticker}", response_model=APIResponse)
async def get_stock(ticker: str, db: Session = Depends(get_db)):
    """
    종목 상세 정보 조회
    
    - **ticker**: 종목 코드
    """
    # 캐시 키 생성
    cache_key = _get_stock_cache_key(ticker)
    
    # 캐시에서 조회 시도
    cached_data = get_cache(cache_key)
    if cached_data is not None:
        return APIResponse(
            success=True,
            data=cached_data,
            message="",
            timestamp=datetime.now(),
        )
    
    # 데이터베이스에서 조회
    stock = db.query(Stock).filter(Stock.ticker == ticker).first()

    if not stock:
        raise NotFoundException(detail=f"Stock with ticker '{ticker}' not found")
    
    # 스키마로 변환
    stock_response = StockResponse.model_validate(stock)
    
    # 캐시에 저장
    set_cache(cache_key, stock_response.model_dump(), CACHE_TTL)

    return APIResponse(
        success=True,
        data=stock_response.model_dump(),
        message="",
        timestamp=datetime.now(),
    )

