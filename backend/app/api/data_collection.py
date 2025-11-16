"""
데이터 수집 API 라우터

Naver Finance에서 가격 데이터, 매매 동향 데이터, 뉴스 데이터를 수집하는 API를 제공합니다.
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, date

from app.database import get_db
from app.models.stock import Stock
from app.collectors.finance_collector import FinanceCollector
from app.collectors.news_collector import NewsCollector
from app.schemas.response import APIResponse
from app.exceptions import NotFoundException, BadRequestException
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/prices/{ticker}", response_model=APIResponse)
async def collect_prices(
    ticker: str,
    days: int = Query(10, ge=1, le=365, description="수집할 일수 (기본: 10일, 최대: 365일)"),
    db: Session = Depends(get_db),
):
    """
    가격 데이터 수집 API
    
    Naver Finance에서 지정된 종목의 가격 데이터를 수집하여 데이터베이스에 저장합니다.
    
    - **ticker**: 종목 코드
    - **days**: 수집할 일수 (1-365일, 기본: 10일)
    
    **Example Request:**
    ```
    POST /api/data/collect/prices/487240?days=10
    ```
    
    **Example Response:**
    ```json
    {
      "success": true,
      "data": {
        "ticker": "487240",
        "saved_count": 10,
        "days": 10
      },
      "message": "Price data collected successfully",
      "timestamp": "2025-11-14T10:30:00"
    }
    ```
    
    **Status Codes:**
    - 200: 성공
    - 404: 종목을 찾을 수 없음
    - 400: 잘못된 파라미터
    - 500: 서버 오류
    """
    try:
        # 종목 존재 확인
        stock = db.query(Stock).filter(Stock.ticker == ticker).first()
        if not stock:
            raise NotFoundException(detail=f"Stock with ticker '{ticker}' not found")
        
        # 데이터 수집기 초기화
        collector = FinanceCollector()
        
        # 가격 데이터 수집 및 저장
        saved_count = collector.collect_and_save_prices(db, ticker, days)
        
        logger.info(f"Price data collection completed for {ticker}: {saved_count} records saved")
        
        return APIResponse(
            success=True,
            data={
                "ticker": ticker,
                "saved_count": saved_count,
                "days": days
            },
            message=f"Price data collected successfully. {saved_count} records saved.",
            timestamp=datetime.now(),
        )
    
    except NotFoundException:
        raise
    except BadRequestException:
        raise
    except Exception as e:
        logger.error(f"Error collecting price data for {ticker}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to collect price data: {str(e)}"
        )


@router.post("/trading/{ticker}", response_model=APIResponse)
async def collect_trading_flow(
    ticker: str,
    days: int = Query(10, ge=1, le=365, description="수집할 일수 (기본: 10일, 최대: 365일)"),
    start_date: Optional[str] = Query(None, description="시작 날짜 (YYYY-MM-DD)", example="2025-01-01"),
    end_date: Optional[str] = Query(None, description="종료 날짜 (YYYY-MM-DD)", example="2025-12-31"),
    db: Session = Depends(get_db),
):
    """
    매매 동향 데이터 수집 API
    
    Naver Finance에서 지정된 종목의 매매 동향 데이터를 수집하여 데이터베이스에 저장합니다.
    
    - **ticker**: 종목 코드
    - **days**: 수집할 일수 (1-365일, 기본: 10일)
    - **start_date**: 시작 날짜 (YYYY-MM-DD 형식, 선택사항)
    - **end_date**: 종료 날짜 (YYYY-MM-DD 형식, 선택사항)
    
    **Example Request:**
    ```
    POST /api/data/collect/trading/487240?days=10
    ```
    
    **Example Response:**
    ```json
    {
      "success": true,
      "data": {
        "ticker": "487240",
        "saved_count": 10,
        "days": 10
      },
      "message": "Trading flow data collected successfully",
      "timestamp": "2025-11-14T10:30:00"
    }
    ```
    
    **Status Codes:**
    - 200: 성공
    - 404: 종목을 찾을 수 없음
    - 400: 잘못된 파라미터
    - 500: 서버 오류
    """
    try:
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
        
        # 데이터 수집기 초기화
        collector = FinanceCollector()
        
        # 매매 동향 데이터 수집 및 저장
        saved_count = collector.collect_and_save_trading_flow(
            db, ticker, days, start_date_obj, end_date_obj
        )
        
        logger.info(f"Trading flow data collection completed for {ticker}: {saved_count} records saved")
        
        return APIResponse(
            success=True,
            data={
                "ticker": ticker,
                "saved_count": saved_count,
                "days": days,
                "start_date": start_date,
                "end_date": end_date
            },
            message=f"Trading flow data collected successfully. {saved_count} records saved.",
            timestamp=datetime.now(),
        )
    
    except NotFoundException:
        raise
    except BadRequestException:
        raise
    except Exception as e:
        logger.error(f"Error collecting trading flow data for {ticker}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to collect trading flow data: {str(e)}"
        )


@router.post("/news/{ticker}", response_model=APIResponse)
async def collect_news(
    ticker: str,
    max_items: int = Query(50, ge=1, le=200, description="최대 수집할 뉴스 개수 (기본: 50개, 최대: 200개)"),
    db: Session = Depends(get_db),
):
    """
    뉴스 데이터 수집 API
    
    Naver Finance에서 지정된 종목의 뉴스 데이터를 수집하여 데이터베이스에 저장합니다.
    
    - **ticker**: 종목 코드
    - **max_items**: 최대 수집할 뉴스 개수 (1-200개, 기본: 50개)
    
    **Example Request:**
    ```
    POST /api/data/collect/news/487240?max_items=50
    ```
    
    **Example Response:**
    ```json
    {
      "success": true,
      "data": {
        "ticker": "487240",
        "saved_count": 50,
        "max_items": 50
      },
      "message": "News data collected successfully",
      "timestamp": "2025-11-14T10:30:00"
    }
    ```
    
    **Status Codes:**
    - 200: 성공
    - 404: 종목을 찾을 수 없음
    - 400: 잘못된 파라미터
    - 500: 서버 오류
    """
    try:
        # 종목 존재 확인
        stock = db.query(Stock).filter(Stock.ticker == ticker).first()
        if not stock:
            raise NotFoundException(detail=f"Stock with ticker '{ticker}' not found")
        
        # 데이터 수집기 초기화
        collector = NewsCollector()
        
        # 뉴스 데이터 수집 및 저장
        saved_count = collector.collect_and_save_news(db, ticker, max_items)
        
        logger.info(f"News data collection completed for {ticker}: {saved_count} records saved")
        
        return APIResponse(
            success=True,
            data={
                "ticker": ticker,
                "saved_count": saved_count,
                "max_items": max_items
            },
            message=f"News data collected successfully. {saved_count} records saved.",
            timestamp=datetime.now(),
        )
    
    except NotFoundException:
        raise
    except BadRequestException:
        raise
    except Exception as e:
        logger.error(f"Error collecting news data for {ticker}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to collect news data: {str(e)}"
        )

