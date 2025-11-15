"""Price 관련 스키마"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime, date
from decimal import Decimal


class PriceBase(BaseModel):
    """Price 기본 스키마"""
    
    ticker: str = Field(..., description="종목 코드", example="034020")
    date: date = Field(..., description="거래일", example="2025-11-13")
    timestamp: datetime = Field(..., description="수집 시각", example="2025-11-13T15:30:00Z")
    current_price: Decimal = Field(..., description="현재가", alias="currentPrice", example=83100)
    change_rate: Optional[Decimal] = Field(None, description="등락률 (%)", alias="changeRate", example=2.5)
    change_amount: Optional[Decimal] = Field(None, description="등락액", alias="changeAmount", example=2025)
    open_price: Optional[Decimal] = Field(None, description="시가", alias="openPrice", example=82000)
    high_price: Optional[Decimal] = Field(None, description="고가", alias="highPrice", example=83500)
    low_price: Optional[Decimal] = Field(None, description="저가", alias="lowPrice", example=81800)
    volume: Optional[Decimal] = Field(None, description="거래량", example=7900000)
    weekly_change_rate: Optional[Decimal] = Field(None, description="주간 등락률 (%)", alias="weeklyChangeRate", example=5.2)
    previous_close: Optional[Decimal] = Field(None, description="전일 종가", alias="previousClose", example=81075)


class PriceResponse(PriceBase):
    """Price 응답 스키마"""
    
    id: int = Field(..., description="고유 ID", example=1)
    
    class Config:
        from_attributes = True
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "ticker": "034020",
                "date": "2025-11-13",
                "timestamp": "2025-11-13T15:30:00Z",
                "currentPrice": 83100,
                "changeRate": 2.5,
                "changeAmount": 2025,
                "openPrice": 82000,
                "highPrice": 83500,
                "lowPrice": 81800,
                "volume": 7900000,
                "weeklyChangeRate": 5.2,
                "previousClose": 81075
            }
        }


class PriceListResponse(BaseModel):
    """Price 목록 응답 스키마"""
    
    prices: List[PriceResponse]
    total: int = Field(..., description="전체 개수", example=100)
    limit: Optional[int] = Field(None, description="페이지 크기", example=100)
    offset: Optional[int] = Field(None, description="오프셋", example=0)

