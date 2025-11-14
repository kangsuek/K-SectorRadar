"""가격 데이터 API 라우터"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db

router = APIRouter()


@router.get("/{ticker}/price")
async def get_price(
    ticker: str,
    date: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """가격 데이터 조회"""
    # TODO: 구현 필요
    return {
        "success": True,
        "data": {},
        "message": "",
        "timestamp": None,
    }

