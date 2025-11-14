"""차트 데이터 API 라우터"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db

router = APIRouter()


@router.get("/{ticker}/chart")
async def get_chart(
    ticker: str,
    days: int = 6,
    db: Session = Depends(get_db),
):
    """차트 데이터 조회"""
    # TODO: 구현 필요
    if days > 30:
        days = 30
    
    return {
        "success": True,
        "data": {
            "ticker": ticker,
            "date": None,  # TODO: 현재 날짜
            "data": [],
        },
        "message": "",
        "timestamp": None,
    }

