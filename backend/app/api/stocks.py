"""주식 정보 API 라우터"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models.stock import Stock
from app.schemas.stock import StockResponse, StockListResponse, StockCreate, StockUpdate
from app.schemas.response import APIResponse
from app.exceptions import NotFoundException, BadRequestException
from app.utils.cache import get_cache, set_cache, invalidate_stock_cache, invalidate_all_stocks_cache, clear_cache_pattern

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
    set_cache(cache_key, stock_list.model_dump(by_alias=True), CACHE_TTL)

    return APIResponse(
        success=True,
        data=stock_list.model_dump(by_alias=True),
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
    set_cache(cache_key, stock_response.model_dump(by_alias=True), CACHE_TTL)

    return APIResponse(
        success=True,
        data=stock_response.model_dump(by_alias=True),
        message="",
        timestamp=datetime.now(),
    )


@router.post("", response_model=APIResponse, status_code=201)
async def create_stock(
    stock_data: StockCreate,
    db: Session = Depends(get_db),
):
    """
    종목 추가 API (관리자용)
    
    새로운 종목을 데이터베이스에 추가합니다.
    
    - **ticker**: 종목 코드 (필수, 고유값)
    - **name**: 종목명 (필수)
    - **type**: 종목 유형 (STOCK/ETF, 필수)
    - **theme**: 테마 분류 (선택사항)
    - **fee**: 수수료 (ETF만 해당, 선택사항)
    
    **Example Request:**
    ```json
    {
      "ticker": "034020",
      "name": "두산에너빌리티",
      "type": "STOCK",
      "theme": "Nuclear/Power Plant/Energy",
      "fee": null
    }
    ```
    
    **Status Codes:**
    - 201: 성공적으로 생성됨
    - 400: 잘못된 요청 (중복된 ticker, 잘못된 type 등)
    - 500: 서버 오류
    """
    try:
        # 기존 종목 확인
        existing = db.query(Stock).filter(Stock.ticker == stock_data.ticker).first()
        if existing:
            raise BadRequestException(
                detail=f"Stock with ticker '{stock_data.ticker}' already exists",
                error_code="DUPLICATE_TICKER",
            )
        
        # type 검증
        if stock_data.type not in ["STOCK", "ETF"]:
            raise BadRequestException(
                detail=f"Invalid stock type: {stock_data.type}. Must be 'STOCK' or 'ETF'",
                error_code="INVALID_STOCK_TYPE",
            )
        
        # 새 종목 생성
        new_stock = Stock(
            ticker=stock_data.ticker,
            name=stock_data.name,
            type=stock_data.type,
            theme=stock_data.theme,
            fee=stock_data.fee,
        )
        
        db.add(new_stock)
        db.commit()
        db.refresh(new_stock)
        
        # 캐시 무효화 (종목 목록 캐시)
        invalidate_all_stocks_cache()
        
        # 응답 생성
        stock_response = StockResponse.model_validate(new_stock)
        
        return APIResponse(
            success=True,
            data=stock_response.model_dump(by_alias=True),
            message=f"Stock '{stock_data.ticker}' created successfully",
            timestamp=datetime.now(),
        )
    
    except BadRequestException:
        raise
    except IntegrityError as e:
        db.rollback()
        raise BadRequestException(
            detail=f"Failed to create stock: {str(e)}",
            error_code="DATABASE_ERROR",
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create stock: {str(e)}"
        )


@router.put("/{ticker}", response_model=APIResponse)
async def update_stock(
    ticker: str,
    stock_data: StockUpdate,
    db: Session = Depends(get_db),
):
    """
    종목 정보 수정 API (관리자용)
    
    기존 종목의 정보를 수정합니다.
    
    - **ticker**: 종목 코드 (경로 파라미터)
    - **name**: 종목명 (선택사항)
    - **type**: 종목 유형 (STOCK/ETF, 선택사항)
    - **theme**: 테마 분류 (선택사항)
    - **fee**: 수수료 (ETF만 해당, 선택사항)
    
    **Example Request:**
    ```json
    {
      "name": "두산에너빌리티 (수정)",
      "theme": "Nuclear/Power Plant/Energy/Updated"
    }
    ```
    
    **Status Codes:**
    - 200: 성공
    - 404: 종목을 찾을 수 없음
    - 400: 잘못된 요청 (잘못된 type 등)
    - 500: 서버 오류
    """
    try:
        # 종목 조회
        stock = db.query(Stock).filter(Stock.ticker == ticker).first()
        if not stock:
            raise NotFoundException(detail=f"Stock with ticker '{ticker}' not found")
        
        # type 검증 (제공된 경우)
        if stock_data.type is not None and stock_data.type not in ["STOCK", "ETF"]:
            raise BadRequestException(
                detail=f"Invalid stock type: {stock_data.type}. Must be 'STOCK' or 'ETF'",
                error_code="INVALID_STOCK_TYPE",
            )
        
        # 업데이트할 필드만 수정
        if stock_data.name is not None:
            stock.name = stock_data.name
        if stock_data.type is not None:
            stock.type = stock_data.type
        if stock_data.theme is not None:
            stock.theme = stock_data.theme
        if stock_data.fee is not None:
            stock.fee = stock_data.fee
        
        db.commit()
        db.refresh(stock)
        
        # 캐시 무효화
        invalidate_stock_cache(ticker)
        invalidate_all_stocks_cache()
        
        # 응답 생성
        stock_response = StockResponse.model_validate(stock)
        
        return APIResponse(
            success=True,
            data=stock_response.model_dump(by_alias=True),
            message=f"Stock '{ticker}' updated successfully",
            timestamp=datetime.now(),
        )
    
    except NotFoundException:
        raise
    except BadRequestException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update stock: {str(e)}"
        )


@router.delete("/{ticker}", response_model=APIResponse)
async def delete_stock(
    ticker: str,
    db: Session = Depends(get_db),
):
    """
    종목 삭제 API (관리자용)
    
    종목을 데이터베이스에서 삭제합니다.
    
    - **ticker**: 종목 코드 (경로 파라미터)
    
    **Status Codes:**
    - 200: 성공
    - 404: 종목을 찾을 수 없음
    - 500: 서버 오류
    
    **Note**: 종목 삭제 시 관련된 가격 데이터, 매매 동향 데이터, 뉴스 데이터는 별도로 처리해야 할 수 있습니다.
    """
    try:
        # 종목 조회
        stock = db.query(Stock).filter(Stock.ticker == ticker).first()
        if not stock:
            raise NotFoundException(detail=f"Stock with ticker '{ticker}' not found")
        
        # 종목 삭제
        db.delete(stock)
        db.commit()
        
        # 캐시 무효화
        invalidate_stock_cache(ticker)
        invalidate_all_stocks_cache()
        
        return APIResponse(
            success=True,
            data={"ticker": ticker},
            message=f"Stock '{ticker}' deleted successfully",
            timestamp=datetime.now(),
        )
    
    except NotFoundException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete stock: {str(e)}"
        )

