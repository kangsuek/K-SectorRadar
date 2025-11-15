"""종목 API 테스트"""

import pytest
from datetime import datetime
from decimal import Decimal
from unittest.mock import patch

from app.models.stock import Stock


class TestGetStocks:
    """종목 목록 조회 API 테스트"""
    
    def test_get_stocks_empty(self, client):
        """빈 종목 목록 조회 테스트"""
        response = client.get("/api/stocks")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "data" in data
        assert data["data"]["total"] == 0
        assert data["data"]["stocks"] == []
    
    def test_get_stocks_with_data(self, client, db_session):
        """데이터가 있는 종목 목록 조회 테스트"""
        # 테스트 데이터 생성
        stocks = [
            Stock(ticker="TEST001", name="테스트 종목1", type="STOCK", theme="테마1"),
            Stock(ticker="TEST002", name="테스트 종목2", type="ETF", theme="테마2"),
            Stock(ticker="TEST003", name="테스트 종목3", type="STOCK", theme="테마1"),
        ]
        for stock in stocks:
            db_session.add(stock)
        db_session.commit()
        
        response = client.get("/api/stocks")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["data"]["total"] == 3
        assert len(data["data"]["stocks"]) == 3
    
    def test_get_stocks_with_type_filter(self, client, db_session):
        """종목 유형 필터링 테스트"""
        # 테스트 데이터 생성
        stocks = [
            Stock(ticker="STOCK001", name="주식1", type="STOCK"),
            Stock(ticker="STOCK002", name="주식2", type="STOCK"),
            Stock(ticker="ETF001", name="ETF1", type="ETF"),
        ]
        for stock in stocks:
            db_session.add(stock)
        db_session.commit()
        
        # STOCK 타입만 조회
        response = client.get("/api/stocks?type=STOCK")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["data"]["total"] == 2
        assert all(stock["type"] == "STOCK" for stock in data["data"]["stocks"])
    
    def test_get_stocks_with_theme_filter(self, client, db_session):
        """테마 필터링 테스트"""
        # 테스트 데이터 생성
        stocks = [
            Stock(ticker="T001", name="종목1", type="STOCK", theme="테마A"),
            Stock(ticker="T002", name="종목2", type="STOCK", theme="테마A"),
            Stock(ticker="T003", name="종목3", type="STOCK", theme="테마B"),
        ]
        for stock in stocks:
            db_session.add(stock)
        db_session.commit()
        
        # 테마A만 조회
        response = client.get("/api/stocks?theme=테마A")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["data"]["total"] == 2
        assert all(stock["theme"] == "테마A" for stock in data["data"]["stocks"])
    
    def test_get_stocks_with_pagination(self, client, db_session):
        """페이지네이션 테스트"""
        # 테스트 데이터 생성
        stocks = [
            Stock(ticker=f"PAGE{i:03d}", name=f"종목{i}", type="STOCK")
            for i in range(1, 11)
        ]
        for stock in stocks:
            db_session.add(stock)
        db_session.commit()
        
        # limit=5, offset=0
        response = client.get("/api/stocks?limit=5&offset=0")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["data"]["total"] == 10
        assert data["data"]["limit"] == 5
        assert data["data"]["offset"] == 0
        assert len(data["data"]["stocks"]) == 5
        
        # limit=5, offset=5
        response = client.get("/api/stocks?limit=5&offset=5")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["data"]["total"] == 10
        assert len(data["data"]["stocks"]) == 5
    
    @patch('app.api.stocks.get_cache')
    @patch('app.api.stocks.set_cache')
    def test_get_stocks_caching(self, mock_set_cache, mock_get_cache, client, db_session):
        """종목 목록 캐싱 테스트"""
        # 캐시 미스 시뮬레이션
        mock_get_cache.return_value = None
        
        # 테스트 데이터 생성
        stock = Stock(ticker="CACHE001", name="캐시 테스트", type="STOCK")
        db_session.add(stock)
        db_session.commit()
        
        response = client.get("/api/stocks")
        
        assert response.status_code == 200
        # 캐시 저장이 호출되었는지 확인
        assert mock_set_cache.called
    
    @patch('app.api.stocks.get_cache')
    def test_get_stocks_cache_hit(self, mock_get_cache, client):
        """종목 목록 캐시 히트 테스트"""
        # 캐시 히트 시뮬레이션
        cached_data = {
            "stocks": [
                {
                    "ticker": "CACHED001",
                    "name": "캐시된 종목",
                    "type": "STOCK",
                    "theme": None,
                    "fee": None,
                    "createdAt": "2025-01-01T00:00:00",
                    "updatedAt": "2025-01-01T00:00:00",
                }
            ],
            "total": 1,
            "limit": 100,
            "offset": 0,
        }
        mock_get_cache.return_value = cached_data
        
        response = client.get("/api/stocks")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["data"]["total"] == 1
        assert len(data["data"]["stocks"]) == 1
        assert data["data"]["stocks"][0]["ticker"] == "CACHED001"


class TestGetStock:
    """종목 상세 조회 API 테스트"""
    
    def test_get_stock_not_found(self, client):
        """존재하지 않는 종목 조회 테스트"""
        response = client.get("/api/stocks/NONEXISTENT")
        
        assert response.status_code == 404
        data = response.json()
        
        assert data["success"] is False
        assert "error" in data
        assert "NOT_FOUND" in data.get("error_code", "")
    
    def test_get_stock_success(self, client, db_session):
        """종목 상세 조회 성공 테스트"""
        # 테스트 데이터 생성
        stock = Stock(
            ticker="DETAIL001",
            name="상세 조회 테스트",
            type="ETF",
            theme="테스트 테마",
            fee=Decimal("0.15"),
        )
        db_session.add(stock)
        db_session.commit()
        
        response = client.get("/api/stocks/DETAIL001")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "data" in data
        assert data["data"]["ticker"] == "DETAIL001"
        assert data["data"]["name"] == "상세 조회 테스트"
        assert data["data"]["type"] == "ETF"
        assert data["data"]["theme"] == "테스트 테마"
    
    @patch('app.api.stocks.get_cache')
    @patch('app.api.stocks.set_cache')
    def test_get_stock_caching(self, mock_set_cache, mock_get_cache, client, db_session):
        """종목 상세 캐싱 테스트"""
        # 캐시 미스 시뮬레이션
        mock_get_cache.return_value = None
        
        # 테스트 데이터 생성
        stock = Stock(ticker="CACHE002", name="캐시 테스트2", type="STOCK")
        db_session.add(stock)
        db_session.commit()
        
        response = client.get("/api/stocks/CACHE002")
        
        assert response.status_code == 200
        # 캐시 저장이 호출되었는지 확인
        assert mock_set_cache.called
    
    @patch('app.api.stocks.get_cache')
    def test_get_stock_cache_hit(self, mock_get_cache, client):
        """종목 상세 캐시 히트 테스트"""
        # 캐시 히트 시뮬레이션
        cached_data = {
            "ticker": "CACHED002",
            "name": "캐시된 종목 상세",
            "type": "STOCK",
            "theme": None,
            "fee": None,
            "createdAt": "2025-01-01T00:00:00",
            "updatedAt": "2025-01-01T00:00:00",
        }
        mock_get_cache.return_value = cached_data
        
        response = client.get("/api/stocks/CACHED002")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["data"]["ticker"] == "CACHED002"
        assert data["data"]["name"] == "캐시된 종목 상세"


class TestStocksAPIErrorHandling:
    """종목 API 에러 핸들링 테스트"""
    
    def test_get_stocks_invalid_query_params(self, client):
        """잘못된 쿼리 파라미터 테스트"""
        # limit이 음수인 경우 (FastAPI가 자동으로 검증)
        response = client.get("/api/stocks?limit=-1")
        
        # FastAPI는 자동으로 검증하므로 422 또는 200일 수 있음
        assert response.status_code in [200, 422]
    
    def test_get_stock_invalid_ticker_format(self, client):
        """잘못된 ticker 형식 테스트"""
        # ticker는 문자열이므로 형식 검증은 없지만, 존재하지 않으면 404
        response = client.get("/api/stocks/")
        
        # 경로가 잘못되었으므로 404 또는 422
        assert response.status_code in [404, 422]

