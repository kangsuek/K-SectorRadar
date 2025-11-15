"""Stock 관련 스키마"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal


class StockBase(BaseModel):
    """Stock 기본 스키마"""
    
    ticker: str = Field(..., description="종목 코드", example="034020")
    name: str = Field(..., description="종목명", example="두산에너빌리티")
    type: str = Field(..., description="종목 유형 (STOCK/ETF)", example="STOCK")
    theme: Optional[str] = Field(None, description="테마 분류", example="Nuclear/Power Plant/Energy")
    fee: Optional[Decimal] = Field(None, description="수수료 (ETF만 해당)", example=None)


class StockResponse(StockBase):
    """Stock 응답 스키마"""
    
    created_at: datetime = Field(..., description="생성일시", alias="createdAt")
    updated_at: datetime = Field(..., description="수정일시", alias="updatedAt")
    
    class Config:
        from_attributes = True
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "ticker": "034020",
                "name": "두산에너빌리티",
                "type": "STOCK",
                "theme": "Nuclear/Power Plant/Energy",
                "fee": None,
                "createdAt": "2025-01-01T00:00:00Z",
                "updatedAt": "2025-11-13T21:22:11Z"
            }
        }


class StockListResponse(BaseModel):
    """Stock 목록 응답 스키마"""
    
    stocks: List[StockResponse]
    total: int = Field(..., description="전체 개수", example=100)
    limit: int = Field(..., description="페이지 크기", example=100)
    offset: int = Field(..., description="오프셋", example=0)

