"""뉴스 데이터 API 라우터"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db

router = APIRouter()


@router.get("/{ticker}/news")
async def get_news(
    ticker: str,
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """뉴스 목록 조회"""
    # TODO: 구현 필요
    return {
        "success": True,
        "data": {
            "news": [],
            "total": 0,
            "limit": limit,
            "offset": offset,
        },
        "message": "",
        "timestamp": None,
    }

