"""데이터 갱신 API 라우터"""

from fastapi import APIRouter
from typing import List, Optional

router = APIRouter()


@router.post("/api/refresh")
async def refresh_data(tickers: Optional[List[str]] = None):
    """데이터 수동 갱신"""
    # TODO: 구현 필요
    return {
        "success": True,
        "data": {
            "updated": 0,
            "failed": 0,
            "tickers": tickers or [],
        },
        "message": "Data refresh completed.",
        "timestamp": None,
    }

