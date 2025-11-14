"""주식 정보 API 라우터"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.stock import Stock

router = APIRouter()


@router.get("")
async def get_stocks(
    type: Optional[str] = None,
    theme: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """주식 목록 조회"""
    query = db.query(Stock)

    if type:
        query = query.filter(Stock.type == type)
    if theme:
        query = query.filter(Stock.theme == theme)

    total = query.count()
    stocks = query.offset(offset).limit(limit).all()

    return {
        "success": True,
        "data": {
            "stocks": stocks,
            "total": total,
            "limit": limit,
            "offset": offset,
        },
        "message": "",
        "timestamp": None,  # TODO: 현재 시간 추가
    }


@router.get("/{ticker}")
async def get_stock(ticker: str, db: Session = Depends(get_db)):
    """주식 상세 정보 조회"""
    stock = db.query(Stock).filter(Stock.ticker == ticker).first()

    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")

    return {
        "success": True,
        "data": stock,
        "message": "",
        "timestamp": None,  # TODO: 현재 시간 추가
    }

