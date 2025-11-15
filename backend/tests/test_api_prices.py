"""가격 데이터 API 테스트"""

import pytest
from datetime import datetime, date
from decimal import Decimal
from unittest.mock import patch

from app.models.stock import Stock
from app.models.price import Price


class TestGetPrice:
    """가격 데이터 조회 API 테스트"""
    
    def test_get_price_stock_not_found(self, client):
        """존재하지 않는 종목의 가격 데이터 조회 테스트"""
        response = client.get("/api/prices/NONEXISTENT")
        
        assert response.status_code == 404
        data = response.json()
        
        assert data["success"] is False
        assert "error" in data
        assert "NOT_FOUND" in data.get("error_code", "")
    
    def test_get_price_empty(self, client, db_session):
        """가격 데이터가 없는 경우 테스트"""
        # 종목만 생성
        stock = Stock(ticker="EMPTY001", name="빈 가격 종목", type="STOCK")
        db_session.add(stock)
        db_session.commit()
        
        response = client.get("/api/prices/EMPTY001")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["data"]["total"] == 0
        assert data["data"]["prices"] == []
    
    def test_get_price_success(self, client, db_session):
        """가격 데이터 조회 성공 테스트"""
        # 종목 생성
        stock = Stock(ticker="PRICE001", name="가격 테스트 종목", type="STOCK")
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
        
        response = client.get("/api/prices/PRICE001")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["data"]["total"] == 1
        assert len(data["data"]["prices"]) == 1
        
        price_data = data["data"]["prices"][0]
        assert price_data["ticker"] == "PRICE001"
        assert float(price_data["currentPrice"]) == 100000
        assert float(price_data["changeRate"]) == 2.5
    
    def test_get_price_with_date_range(self, client, db_session):
        """날짜 범위로 가격 데이터 조회 테스트"""
        # 종목 생성
        stock = Stock(ticker="DATERANGE001", name="날짜 범위 테스트", type="STOCK")
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
        response = client.get(
            "/api/prices/DATERANGE001?start_date=2025-01-02&end_date=2025-01-04"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["data"]["total"] == 3
        assert len(data["data"]["prices"]) == 3
        
        # 날짜 확인
        dates = [p["date"] for p in data["data"]["prices"]]
        assert "2025-01-02" in dates
        assert "2025-01-03" in dates
        assert "2025-01-04" in dates
    
    def test_get_price_with_start_date_only(self, client, db_session):
        """시작 날짜만 지정한 경우 테스트"""
        # 종목 생성
        stock = Stock(ticker="STARTDATE001", name="시작일 테스트", type="STOCK")
        db_session.add(stock)
        db_session.commit()
        
        # 가격 데이터 생성
        prices = [
            Price(
                ticker="STARTDATE001",
                date=date(2025, 1, i),
                timestamp=datetime(2025, 1, i, 15, 30, 0),
                current_price=Decimal("100000"),
            )
            for i in range(1, 4)
        ]
        for price in prices:
            db_session.add(price)
        db_session.commit()
        
        response = client.get("/api/prices/STARTDATE001?start_date=2025-01-02")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["data"]["total"] == 2  # 1월 2일, 3일
        assert all(
            p["date"] >= "2025-01-02" for p in data["data"]["prices"]
        )
    
    def test_get_price_with_end_date_only(self, client, db_session):
        """종료 날짜만 지정한 경우 테스트"""
        # 종목 생성
        stock = Stock(ticker="ENDDATE001", name="종료일 테스트", type="STOCK")
        db_session.add(stock)
        db_session.commit()
        
        # 가격 데이터 생성
        prices = [
            Price(
                ticker="ENDDATE001",
                date=date(2025, 1, i),
                timestamp=datetime(2025, 1, i, 15, 30, 0),
                current_price=Decimal("100000"),
            )
            for i in range(1, 4)
        ]
        for price in prices:
            db_session.add(price)
        db_session.commit()
        
        response = client.get("/api/prices/ENDDATE001?end_date=2025-01-02")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["data"]["total"] == 2  # 1월 1일, 2일
        assert all(
            p["date"] <= "2025-01-02" for p in data["data"]["prices"]
        )
    
    def test_get_price_with_pagination(self, client, db_session):
        """페이지네이션 테스트"""
        # 종목 생성
        stock = Stock(ticker="PAGE001", name="페이지네이션 테스트", type="STOCK")
        db_session.add(stock)
        db_session.commit()
        
        # 가격 데이터 생성
        prices = [
            Price(
                ticker="PAGE001",
                date=date(2025, 1, i),
                timestamp=datetime(2025, 1, i, 15, 30, 0),
                current_price=Decimal("100000"),
            )
            for i in range(1, 11)
        ]
        for price in prices:
            db_session.add(price)
        db_session.commit()
        
        # limit=5, offset=0
        response = client.get("/api/prices/PAGE001?limit=5&offset=0")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["data"]["total"] == 10
        assert data["data"]["limit"] == 5
        assert data["data"]["offset"] == 0
        assert len(data["data"]["prices"]) == 5
    
    def test_get_price_invalid_date_format(self, client, db_session):
        """잘못된 날짜 형식 테스트"""
        # 종목 생성
        stock = Stock(ticker="INVALID001", name="잘못된 날짜 테스트", type="STOCK")
        db_session.add(stock)
        db_session.commit()
        
        # 잘못된 날짜 형식
        response = client.get("/api/prices/INVALID001?start_date=2025/01/01")
        
        assert response.status_code == 400
        data = response.json()
        
        assert data["success"] is False
        assert "INVALID_DATE_FORMAT" in data.get("error_code", "")
    
    def test_get_price_invalid_date_range(self, client, db_session):
        """잘못된 날짜 범위 테스트 (start_date > end_date)"""
        # 종목 생성
        stock = Stock(ticker="INVALID002", name="잘못된 범위 테스트", type="STOCK")
        db_session.add(stock)
        db_session.commit()
        
        # start_date가 end_date보다 큰 경우
        response = client.get(
            "/api/prices/INVALID002?start_date=2025-01-10&end_date=2025-01-01"
        )
        
        assert response.status_code == 400
        data = response.json()
        
        assert data["success"] is False
        assert "INVALID_DATE_RANGE" in data.get("error_code", "")
    
    @patch('app.api.prices.get_cache')
    @patch('app.api.prices.set_cache')
    def test_get_price_caching(self, mock_set_cache, mock_get_cache, client, db_session):
        """가격 데이터 캐싱 테스트"""
        # 캐시 미스 시뮬레이션
        mock_get_cache.return_value = None
        
        # 종목 및 가격 데이터 생성
        stock = Stock(ticker="CACHE001", name="캐시 테스트", type="STOCK")
        db_session.add(stock)
        db_session.commit()

        price = Price(
            ticker="CACHE001",
            date=date(2025, 1, 1),
            timestamp=datetime(2025, 1, 1, 15, 30, 0),
            current_price=Decimal("100000"),
        )
        db_session.add(price)
        db_session.commit()
        
        response = client.get("/api/prices/CACHE001")
        
        assert response.status_code == 200
        # 캐시 저장이 호출되었는지 확인
        assert mock_set_cache.called
    
    @patch('app.api.prices.get_cache')
    def test_get_price_cache_hit(self, mock_get_cache, client, db_session):
        """가격 데이터 캐시 히트 테스트"""
        # 종목 생성 (API가 종목 존재를 먼저 확인하므로 필요)
        stock = Stock(ticker="CACHED001", name="캐시 테스트 종목", type="STOCK")
        db_session.add(stock)
        db_session.commit()

        # 캐시 히트 시뮬레이션
        cached_data = {
            "prices": [
                {
                    "id": 1,
                    "ticker": "CACHED001",
                    "date": "2025-01-01",
                    "timestamp": "2025-01-01T15:30:00",
                    "currentPrice": "100000.00",
                    "changeRate": "2.50",
                    "changeAmount": "2500.00",
                    "openPrice": "98000.00",
                    "highPrice": "102000.00",
                    "lowPrice": "97500.00",
                    "volume": "1000000.00",
                }
            ],
            "total": 1,
            "limit": None,
            "offset": 0,
        }
        mock_get_cache.return_value = cached_data
        
        response = client.get("/api/prices/CACHED001")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["data"]["total"] == 1
        assert len(data["data"]["prices"]) == 1
        assert data["data"]["prices"][0]["ticker"] == "CACHED001"
        assert float(data["data"]["prices"][0]["currentPrice"]) == 100000
    
    def test_get_price_ordering(self, client, db_session):
        """가격 데이터 정렬 테스트 (최신순)"""
        # 종목 생성
        stock = Stock(ticker="ORDER001", name="정렬 테스트", type="STOCK")
        db_session.add(stock)
        db_session.commit()
        
        # 가격 데이터 생성 (날짜 역순)
        prices = [
            Price(
                ticker="ORDER001",
                date=date(2025, 1, i),
                timestamp=datetime(2025, 1, i, 15, 30, 0),
                current_price=Decimal("100000"),
            )
            for i in range(1, 4)
        ]
        for price in prices:
            db_session.add(price)
        db_session.commit()
        
        response = client.get("/api/prices/ORDER001")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        # 최신순으로 정렬되어야 함 (날짜 내림차순)
        dates = [p["date"] for p in data["data"]["prices"]]
        assert dates == sorted(dates, reverse=True)

