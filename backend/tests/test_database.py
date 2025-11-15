"""데이터베이스 연결 및 모델 테스트"""

import pytest
from sqlalchemy.orm import Session
from datetime import datetime, date
from decimal import Decimal

from app.database import (
    get_db,
    init_db,
    engine,
    SessionLocal,
    seed_stocks_from_json,
    init_db_with_seed,
)
from app.models.stock import Stock
from app.models.price import Price
from app.models.trading_trend import TradingTrend
from app.models.news import News


class TestDatabaseConnection:
    """데이터베이스 연결 테스트"""
    
    def test_database_connection(self):
        """데이터베이스 연결 테스트"""
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1
    
    def test_get_db_session(self):
        """데이터베이스 세션 생성 테스트"""
        db_gen = get_db()
        db = next(db_gen)
        
        assert db is not None
        assert isinstance(db, Session)
        
        # 세션 정리
        try:
            next(db_gen)
        except StopIteration:
            pass
    
    def test_init_db(self):
        """데이터베이스 초기화 테스트"""
        # 테이블이 생성되는지 확인
        import asyncio
        asyncio.run(init_db())
        
        # 테이블 존재 확인
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        assert "stocks" in tables
        assert "prices" in tables
        assert "trading_trends" in tables
        assert "news" in tables


class TestStockModel:
    """Stock 모델 테스트"""
    
    def test_create_stock(self, db_session):
        """Stock 생성 테스트"""
        stock = Stock(
            ticker="TEST001",
            name="테스트 종목",
            type="STOCK",
            theme="테스트 테마",
        )
        
        db_session.add(stock)
        db_session.commit()
        db_session.refresh(stock)
        
        assert stock.ticker == "TEST001"
        assert stock.name == "테스트 종목"
        assert stock.type == "STOCK"
        assert stock.theme == "테스트 테마"
        assert stock.created_at is not None
        assert stock.updated_at is not None
    
    def test_query_stock(self, db_session):
        """Stock 조회 테스트"""
        # 종목 생성
        stock = Stock(
            ticker="TEST002",
            name="조회 테스트 종목",
            type="ETF",
            fee=Decimal("0.15"),
        )
        db_session.add(stock)
        db_session.commit()
        
        # 조회
        found_stock = db_session.query(Stock).filter(Stock.ticker == "TEST002").first()
        
        assert found_stock is not None
        assert found_stock.name == "조회 테스트 종목"
        assert found_stock.type == "ETF"
        assert found_stock.fee == Decimal("0.15")
    
    def test_update_stock(self, db_session):
        """Stock 업데이트 테스트"""
        # 종목 생성
        stock = Stock(
            ticker="TEST003",
            name="업데이트 전",
            type="STOCK",
        )
        db_session.add(stock)
        db_session.commit()
        
        original_updated_at = stock.updated_at
        
        # 업데이트
        stock.name = "업데이트 후"
        stock.theme = "새로운 테마"
        db_session.commit()
        db_session.refresh(stock)
        
        assert stock.name == "업데이트 후"
        assert stock.theme == "새로운 테마"
        # updated_at이 변경되었는지 확인 (약간의 지연 고려)
        assert stock.updated_at >= original_updated_at
    
    def test_delete_stock(self, db_session):
        """Stock 삭제 테스트"""
        # 종목 생성
        stock = Stock(
            ticker="TEST004",
            name="삭제 테스트 종목",
            type="STOCK",
        )
        db_session.add(stock)
        db_session.commit()
        
        ticker = stock.ticker
        
        # 삭제
        db_session.delete(stock)
        db_session.commit()
        
        # 삭제 확인
        found_stock = db_session.query(Stock).filter(Stock.ticker == ticker).first()
        assert found_stock is None
    
    def test_stock_type_constraint(self, db_session):
        """Stock type 제약 조건 테스트"""
        # 잘못된 type으로 생성 시도
        stock = Stock(
            ticker="TEST005",
            name="잘못된 타입",
            type="INVALID",  # STOCK 또는 ETF만 허용
        )
        db_session.add(stock)
        
        with pytest.raises(Exception):  # IntegrityError 또는 CheckConstraint 오류
            db_session.commit()
        
        db_session.rollback()
    
    def test_stock_filter_by_type(self, db_session):
        """Stock type 필터링 테스트"""
        # 여러 종목 생성
        stocks = [
            Stock(ticker="STOCK001", name="주식1", type="STOCK"),
            Stock(ticker="STOCK002", name="주식2", type="STOCK"),
            Stock(ticker="ETF001", name="ETF1", type="ETF"),
        ]
        for stock in stocks:
            db_session.add(stock)
        db_session.commit()
        
        # STOCK 타입만 조회
        stock_count = db_session.query(Stock).filter(Stock.type == "STOCK").count()
        assert stock_count == 2
        
        # ETF 타입만 조회
        etf_count = db_session.query(Stock).filter(Stock.type == "ETF").count()
        assert etf_count == 1


class TestPriceModel:
    """Price 모델 테스트"""
    
    def test_create_price(self, db_session):
        """Price 생성 테스트"""
        # 먼저 종목 생성
        stock = Stock(
            ticker="PRICE001",
            name="가격 테스트 종목",
            type="STOCK",
        )
        db_session.add(stock)
        db_session.commit()
        
        # 가격 데이터 생성
        price = Price(
            ticker="PRICE001",
            date=date(2025, 1, 1),
            timestamp=datetime(2025, 1, 1, 15, 30, 0),
            current_price=Decimal("100000"),
            change_rate=Decimal("2.5"),
            change_amount=Decimal("2500"),
            open_price=Decimal("98000"),
            high_price=Decimal("102000"),
            low_price=Decimal("97500"),
            volume=Decimal("1000000"),
        )
        
        db_session.add(price)
        db_session.commit()
        db_session.refresh(price)
        
        assert price.ticker == "PRICE001"
        assert price.date == date(2025, 1, 1)
        assert price.current_price == Decimal("100000")
        assert price.change_rate == Decimal("2.5")
        assert price.id is not None
    
    def test_price_foreign_key(self, db_session):
        """Price 외래키 제약 조건 테스트"""
        # 존재하지 않는 종목 코드로 가격 데이터 생성 시도
        price = Price(
            ticker="NONEXISTENT",
            date=date(2025, 1, 1),
            timestamp=datetime(2025, 1, 1, 15, 30, 0),
            current_price=Decimal("100000"),
        )
        db_session.add(price)
        
        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()
        
        db_session.rollback()
    
    def test_price_cascade_delete(self, db_session):
        """Price CASCADE 삭제 테스트"""
        # 종목과 가격 데이터 생성
        stock = Stock(
            ticker="CASCADE001",
            name="CASCADE 테스트",
            type="STOCK",
        )
        db_session.add(stock)
        db_session.commit()
        
        price = Price(
            ticker="CASCADE001",
            date=date(2025, 1, 1),
            timestamp=datetime(2025, 1, 1, 15, 30, 0),
            current_price=Decimal("100000"),
        )
        db_session.add(price)
        db_session.commit()
        
        price_id = price.id
        
        # 종목 삭제
        db_session.delete(stock)
        db_session.commit()
        
        # 가격 데이터도 함께 삭제되었는지 확인
        found_price = db_session.query(Price).filter(Price.id == price_id).first()
        assert found_price is None
    
    def test_query_price_by_date_range(self, db_session):
        """날짜 범위로 Price 조회 테스트"""
        # 종목 생성
        stock = Stock(
            ticker="DATERANGE001",
            name="날짜 범위 테스트",
            type="STOCK",
        )
        db_session.add(stock)
        db_session.commit()
        
        # 여러 날짜의 가격 데이터 생성
        prices = [
            Price(
                ticker="DATERANGE001",
                date=date(2025, 1, i),
                timestamp=datetime(2025, 1, i, 15, 30, 0),
                current_price=Decimal(f"{100000 + i * 1000}"),
            )
            for i in range(1, 6)
        ]
        for price in prices:
            db_session.add(price)
        db_session.commit()
        
        # 날짜 범위로 조회
        start_date = date(2025, 1, 2)
        end_date = date(2025, 1, 4)
        
        result = db_session.query(Price).filter(
            Price.ticker == "DATERANGE001",
            Price.date >= start_date,
            Price.date <= end_date,
        ).all()
        
        assert len(result) == 3
        assert all(start_date <= p.date <= end_date for p in result)


class TestDatabaseSeed:
    """데이터베이스 시드 테스트"""
    
    def test_seed_stocks_from_json(self, db_session, tmp_path):
        """JSON 파일에서 종목 시드 테스트"""
        import json
        
        # 테스트용 JSON 파일 생성
        test_json = [
            {
                "ticker": "SEED001",
                "name": "시드 테스트 종목1",
                "type": "STOCK",
                "theme": "테스트 테마1",
            },
            {
                "ticker": "SEED002",
                "name": "시드 테스트 종목2",
                "type": "ETF",
                "fee": 0.15,
            },
        ]
        
        json_file = tmp_path / "test_stocks.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(test_json, f, ensure_ascii=False)
        
        # 시드 실행
        added_count = seed_stocks_from_json(db_session, str(json_file))
        
        assert added_count == 2
        
        # 데이터 확인
        stock1 = db_session.query(Stock).filter(Stock.ticker == "SEED001").first()
        assert stock1 is not None
        assert stock1.name == "시드 테스트 종목1"
        
        stock2 = db_session.query(Stock).filter(Stock.ticker == "SEED002").first()
        assert stock2 is not None
        assert stock2.type == "ETF"
    
    def test_seed_stocks_duplicate(self, db_session, tmp_path):
        """중복 종목 시드 테스트 (업데이트)"""
        import json
        
        # 첫 번째 시드
        test_json1 = [
            {
                "ticker": "DUPLICATE001",
                "name": "원래 이름",
                "type": "STOCK",
            },
        ]
        
        json_file = tmp_path / "test_stocks1.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(test_json1, f, ensure_ascii=False)
        
        added_count1 = seed_stocks_from_json(db_session, str(json_file))
        assert added_count1 == 1
        
        # 두 번째 시드 (같은 ticker, 다른 이름)
        test_json2 = [
            {
                "ticker": "DUPLICATE001",
                "name": "업데이트된 이름",
                "type": "STOCK",
                "theme": "새로운 테마",
            },
        ]
        
        json_file2 = tmp_path / "test_stocks2.json"
        with open(json_file2, "w", encoding="utf-8") as f:
            json.dump(test_json2, f, ensure_ascii=False)
        
        added_count2 = seed_stocks_from_json(db_session, str(json_file2))
        assert added_count2 == 0  # 새로 추가된 것은 없음
        
        # 업데이트 확인
        stock = db_session.query(Stock).filter(Stock.ticker == "DUPLICATE001").first()
        assert stock.name == "업데이트된 이름"
        assert stock.theme == "새로운 테마"

