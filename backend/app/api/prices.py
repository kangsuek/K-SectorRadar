"""가격 데이터 API 라우터"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models.price import Price
from app.models.stock import Stock
from app.schemas.price import PriceResponse, PriceListResponse
from app.schemas.response import APIResponse
from app.exceptions import NotFoundException, BadRequestException
from app.utils.cache import get_cache, set_cache

router = APIRouter()

# 캐시 TTL (초)
CACHE_TTL = 1800  # 30분


def _get_price_cache_key(
    ticker: str,
    start_date: Optional[str],
    end_date: Optional[str],
    limit: Optional[int],
    offset: Optional[int],
) -> str:
    """가격 데이터 캐시 키 생성"""
    key_parts = [f"prices:{ticker}"]
    if start_date:
        key_parts.append(f"start:{start_date}")
    if end_date:
        key_parts.append(f"end:{end_date}")
    if limit:
        key_parts.append(f"limit:{limit}")
    if offset:
        key_parts.append(f"offset:{offset}")
    return ":".join(key_parts)


@router.get("/{ticker}", response_model=APIResponse)
async def get_price(
    ticker: str,
    start_date: Optional[str] = Query(None, description="시작 날짜 (YYYY-MM-DD)", example="2025-01-01"),
    end_date: Optional[str] = Query(None, description="종료 날짜 (YYYY-MM-DD)", example="2025-12-31"),
    limit: Optional[int] = Query(None, description="페이지 크기", example=100),
    offset: Optional[int] = Query(0, description="오프셋", example=0),
    db: Session = Depends(get_db),
):
    """
    종목 가격 데이터 조회
    
    - **ticker**: 종목 코드
    - **start_date**: 시작 날짜 (YYYY-MM-DD 형식, 선택사항)
    - **end_date**: 종료 날짜 (YYYY-MM-DD 형식, 선택사항)
    - **limit**: 페이지 크기 (선택사항)
    - **offset**: 오프셋 (기본값: 0)
    """
    # 종목 존재 확인
    stock = db.query(Stock).filter(Stock.ticker == ticker).first()
    if not stock:
        raise NotFoundException(detail=f"Stock with ticker '{ticker}' not found")
    
    # 날짜 파싱 및 검증
    start_date_obj = None
    end_date_obj = None
    
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        except ValueError:
            raise BadRequestException(
                detail=f"Invalid start_date format. Expected YYYY-MM-DD, got: {start_date}",
                error_code="INVALID_DATE_FORMAT",
            )
    
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            raise BadRequestException(
                detail=f"Invalid end_date format. Expected YYYY-MM-DD, got: {end_date}",
                error_code="INVALID_DATE_FORMAT",
            )
    
    if start_date_obj and end_date_obj and start_date_obj > end_date_obj:
        raise BadRequestException(
            detail="start_date must be before or equal to end_date",
            error_code="INVALID_DATE_RANGE",
        )
    
    # 캐시 키 생성
    cache_key = _get_price_cache_key(ticker, start_date, end_date, limit, offset)
    
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
    query = db.query(Price).filter(Price.ticker == ticker)
    
    # 날짜 범위 필터링
    if start_date_obj:
        query = query.filter(Price.date >= start_date_obj)
    if end_date_obj:
        query = query.filter(Price.date <= end_date_obj)
    
    # 정렬 (날짜 내림차순 - 최신순)
    query = query.order_by(Price.date.desc())
    
    # 전체 개수 조회
    total = query.count()
    
    # 페이지네이션
    if limit:
        query = query.offset(offset).limit(limit)
    
    prices = query.all()
    
    # 스키마로 변환
    price_list = PriceListResponse(
        prices=[PriceResponse.model_validate(price) for price in prices],
        total=total,
        limit=limit,
        offset=offset,
    )
    
    # 캐시에 저장
    set_cache(cache_key, price_list.model_dump(), CACHE_TTL)

    return APIResponse(
        success=True,
        data=price_list.model_dump(),
        message="",
        timestamp=datetime.now(),
    )

