"""데이터베이스 연결 및 초기화"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool, QueuePool
from typing import Generator
import json
import os
from pathlib import Path

from app.config import settings
from app.db_base import Base
# 모델은 순환 import 방지를 위해 init_db() 함수 내에서만 import

# SQLite용 설정
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite는 파일 경로 생성
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=settings.ENVIRONMENT == "development",  # 개발 환경에서만 SQL 로그 출력
    )
else:
    # PostgreSQL/MySQL용 설정
    # 연결 풀 설정
    pool_size = 5
    max_overflow = 10
    pool_timeout = 30
    pool_recycle = 3600  # 1시간마다 연결 재생성
    
    engine = create_engine(
        settings.DATABASE_URL,
        poolclass=QueuePool,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_timeout=pool_timeout,
        pool_recycle=pool_recycle,
        pool_pre_ping=True,  # 연결 상태 확인 후 사용
        echo=settings.ENVIRONMENT == "development",  # 개발 환경에서만 SQL 로그 출력
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


async def init_db():
    """데이터베이스 초기화 - 테이블 생성"""
    # 모든 모델 import (테이블 메타데이터 등록)
    from app.models import Stock, Price, TradingTrend, News
    
    # 테이블 생성
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """데이터베이스 세션 의존성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_stocks_from_json(db: Session, json_path: str = None) -> int:
    """
    JSON 파일에서 종목 데이터를 읽어 데이터베이스에 시드
    
    Args:
        db: 데이터베이스 세션
        json_path: JSON 파일 경로 (기본값: config/stocks.json)
    
    Returns:
        추가된 종목 수
    """
    # 순환 import 방지
    from app.models.stock import Stock
    
    if json_path is None:
        # 기본 경로: backend/config/stocks.json
        base_dir = Path(__file__).parent.parent
        json_path = base_dir / "config" / "stocks.json"
    else:
        json_path = Path(json_path)
    
    if not json_path.exists():
        raise FileNotFoundError(f"Stocks JSON file not found: {json_path}")
    
    with open(json_path, "r", encoding="utf-8") as f:
        stocks_data = json.load(f)
    
    added_count = 0
    for stock_data in stocks_data:
        # 기존 종목 확인
        existing = db.query(Stock).filter(Stock.ticker == stock_data["ticker"]).first()
        if existing:
            # 기존 종목 업데이트
            existing.name = stock_data["name"]
            existing.type = stock_data["type"]
            existing.theme = stock_data.get("theme")
            existing.fee = stock_data.get("fee")
        else:
            # 새 종목 추가
            stock = Stock(
                ticker=stock_data["ticker"],
                name=stock_data["name"],
                type=stock_data["type"],
                theme=stock_data.get("theme"),
                fee=stock_data.get("fee"),
            )
            db.add(stock)
            added_count += 1
    
    db.commit()
    return added_count


def init_db_with_seed(db: Session = None) -> None:
    """
    데이터베이스 초기화 및 시드 데이터 로드
    
    Args:
        db: 데이터베이스 세션 (None이면 새로 생성)
    """
    # 테이블 생성
    Base.metadata.create_all(bind=engine)
    
    # 시드 데이터 로드
    if db is None:
        db = SessionLocal()
        try:
            seed_stocks_from_json(db)
        finally:
            db.close()
    else:
        seed_stocks_from_json(db)


if __name__ == "__main__":
    """데이터베이스 초기화 및 시드 실행"""
    import asyncio
    
    async def main():
        print("데이터베이스 초기화 중...")
        await init_db()
        print("✅ 테이블 생성 완료")
        
        print("종목 데이터 시드 중...")
        db = SessionLocal()
        try:
            added_count = seed_stocks_from_json(db)
            print(f"✅ {added_count}개의 종목이 추가되었습니다.")
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            raise
        finally:
            db.close()
        
        print("✅ 데이터베이스 초기화 완료!")
    
    asyncio.run(main())

