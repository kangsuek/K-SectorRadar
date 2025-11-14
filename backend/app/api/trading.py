"""매매 동향 API 라우터"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db

router = APIRouter()


@router.get("/{ticker}/trading")
async def get_trading(
    ticker: str,
    date: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """매매 동향 데이터 조회"""
    # TODO: 구현 필요
    return {
        "success": True,
        "data": {},
        "message": "",
        "timestamp": None,
    }

