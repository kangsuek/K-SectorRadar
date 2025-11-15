"""통합 테스트 - 데이터베이스 + Redis + API"""

import pytest
from datetime import datetime, date
from decimal import Decimal
from unittest.mock import patch, Mock

from app.models.stock import Stock
from app.models.price import Price
from app.utils.cache import get_cache, set_cache, delete_cache


class TestIntegrationStockAPI:
    """종목 API 통합 테스트"""
    
    def test_stock_lifecycle(self, client, db_session, mock_redis_client):
        """종목 생성 → 조회 → 캐싱 → 무효화 전체 플로우 테스트"""
        # 1. 종목 생성
        stock = Stock(
            ticker="INTEG001",
            name="통합 테스트 종목",
            type="STOCK",
            theme="통합 테스트 테마",
        )
        db_session.add(stock)
        db_session.commit()
        
        # 2. API로 조회 (캐시 미스)
        mock_redis_client.get.return_value = None
        
        response = client.get("/api/stocks/INTEG001")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["ticker"] == "INTEG001"
        
        # 3. 캐시 저장 확인
        assert mock_redis_client.setex.called
        
        # 4. 캐시 히트 시뮬레이션
        cached_data = data["data"]
        import json
        mock_redis_client.get.return_value = json.dumps(cached_data)
        
        # 5. 다시 조회 (캐시 히트)
        response2 = client.get("/api/stocks/INTEG001")
        
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["success"] is True
        assert data2["data"]["ticker"] == "INTEG001"
        
        # 6. 캐시 무효화
        delete_cache("stocks:detail:INTEG001")
        assert mock_redis_client.delete.called
    
    def test_stock_list_with_filtering_and_caching(self, client, db_session, mock_redis_client):
        """종목 목록 조회 + 필터링 + 캐싱 통합 테스트"""
        # 테스트 데이터 생성
        stocks = [
            Stock(ticker="FILTER001", name="필터 테스트1", type="STOCK", theme="테마A"),
            Stock(ticker="FILTER002", name="필터 테스트2", type="STOCK", theme="테마A"),
            Stock(ticker="FILTER003", name="필터 테스트3", type="ETF", theme="테마B"),
        ]
        for stock in stocks:
            db_session.add(stock)
        db_session.commit()
        
        # 캐시 미스
        mock_redis_client.get.return_value = None
        
        # 1. 전체 조회
        response = client.get("/api/stocks")
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["total"] == 3
        
        # 2. 타입 필터링
        response = client.get("/api/stocks?type=STOCK")
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["total"] == 2
        
        # 3. 테마 필터링
        response = client.get("/api/stocks?theme=테마A")
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["total"] == 2


class TestIntegrationPriceAPI:
    """가격 데이터 API 통합 테스트"""
    
    def test_price_data_lifecycle(self, client, db_session, mock_redis_client):
        """가격 데이터 생성 → 조회 → 캐싱 전체 플로우 테스트"""
        # 1. 종목 생성
        stock = Stock(ticker="PRICEINTEG001", name="가격 통합 테스트", type="STOCK")
        db_session.add(stock)
        db_session.commit()
        
        # 2. 가격 데이터 생성
        prices = [
            Price(
                ticker="PRICEINTEG001",
                date=date(2025, 1, i),
                timestamp=datetime(2025, 1, i, 15, 30, 0),
                current_price=Decimal(f"{100000 + i * 1000}"),
                change_rate=Decimal(f"{i * 0.5}"),
            )
            for i in range(1, 6)
        ]
        for price in prices:
            db_session.add(price)
        db_session.commit()
        
        # 3. 캐시 미스
        mock_redis_client.get.return_value = None
        
        # 4. 전체 가격 데이터 조회
        response = client.get("/api/prices/PRICEINTEG001")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total"] == 5
        
        # 5. 날짜 범위로 조회
        response = client.get(
            "/api/prices/PRICEINTEG001?start_date=2025-01-02&end_date=2025-01-04"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total"] == 3
        
        # 6. 캐시 저장 확인
        assert mock_redis_client.setex.called


class TestIntegrationCacheInvalidation:
    """캐시 무효화 통합 테스트"""
    
    def test_cache_invalidation_on_stock_update(self, client, db_session, mock_redis_client):
        """종목 업데이트 시 캐시 무효화 테스트"""
        import json
        
        # 1. 종목 생성 및 조회 (캐시 저장)
        stock = Stock(ticker="INVALID001", name="무효화 테스트", type="STOCK")
        db_session.add(stock)
        db_session.commit()
        
        mock_redis_client.get.return_value = None
        
        response = client.get("/api/stocks/INVALID001")
        assert response.status_code == 200
        
        # 캐시에 저장된 데이터
        cached_data = {
            "ticker": "INVALID001",
            "name": "무효화 테스트",
            "type": "STOCK",
            "theme": None,
            "fee": None,
            "createdAt": "2025-01-01T00:00:00",
            "updatedAt": "2025-01-01T00:00:00",
        }
        mock_redis_client.get.return_value = json.dumps(cached_data)
        
        # 2. 캐시 히트 확인
        response2 = client.get("/api/stocks/INVALID001")
        assert response2.status_code == 200
        
        # 3. 종목 업데이트 (실제로는 API가 없지만, DB에서 직접 업데이트)
        stock.name = "업데이트된 이름"
        db_session.commit()
        
        # 4. 캐시 무효화 (실제로는 API에서 호출)
        from app.utils.cache import invalidate_stock_cache
        invalidate_stock_cache("INVALID001")
        
        # 캐시 삭제가 호출되었는지 확인
        assert mock_redis_client.scan_iter.called or mock_redis_client.delete.called


class TestIntegrationErrorHandling:
    """에러 핸들링 통합 테스트"""
    
    def test_not_found_error_handling(self, client):
        """404 에러 핸들링 테스트"""
        # 존재하지 않는 종목
        response = client.get("/api/stocks/NONEXISTENT")
        
        assert response.status_code == 404
        data = response.json()
        
        assert data["success"] is False
        assert "error" in data
        assert "error_code" in data
        assert data["error_code"] == "NOT_FOUND"
    
    def test_bad_request_error_handling(self, client, db_session):
        """400 에러 핸들링 테스트"""
        # 종목 생성
        stock = Stock(ticker="BADREQ001", name="잘못된 요청 테스트", type="STOCK")
        db_session.add(stock)
        db_session.commit()
        
        # 잘못된 날짜 형식
        response = client.get("/api/prices/BADREQ001?start_date=invalid-date")
        
        assert response.status_code == 400
        data = response.json()
        
        assert data["success"] is False
        assert "error" in data
        assert "INVALID_DATE_FORMAT" in data.get("error_code", "")


class TestIntegrationHealthCheck:
    """Health Check 통합 테스트"""
    
    def test_health_check_with_all_services(self, client, mock_redis_client):
        """모든 서비스가 정상인 경우 Health Check 테스트"""
        # Redis 연결 성공 시뮬레이션
        mock_redis_client.ping.return_value = True
        
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["database"] == "connected"
        # Redis는 모킹되어 있으므로 상태 확인
        assert data["redis"] in ["connected", "disconnected"]
        
        # 데이터베이스가 연결되어 있으면 healthy
        if data["database"] == "connected":
            assert data["status"] == "healthy"


class TestIntegrationFullWorkflow:
    """전체 워크플로우 통합 테스트"""
    
    def test_full_workflow(self, client, db_session, mock_redis_client):
        """전체 워크플로우 테스트: 종목 생성 → 가격 데이터 추가 → 조회 → 캐싱"""
        import json
        
        # 1. 종목 생성
        stock = Stock(
            ticker="WORKFLOW001",
            name="워크플로우 테스트",
            type="STOCK",
            theme="테스트 테마",
        )
        db_session.add(stock)
        db_session.commit()
        
        # 2. 가격 데이터 추가
        price = Price(
            ticker="WORKFLOW001",
            date=date(2025, 1, 1),
            timestamp=datetime(2025, 1, 1, 15, 30, 0),
            current_price=Decimal("100000"),
            change_rate=Decimal("2.5"),
        )
        db_session.add(price)
        db_session.commit()
        
        # 3. Health Check
        response = client.get("/api/health")
        assert response.status_code == 200
        
        # 4. 종목 목록 조회 (캐시 미스)
        mock_redis_client.get.return_value = None
        response = client.get("/api/stocks")
        assert response.status_code == 200
        
        # 5. 종목 상세 조회 (캐시 미스)
        mock_redis_client.get.return_value = None
        response = client.get("/api/stocks/WORKFLOW001")
        assert response.status_code == 200
        stock_data = response.json()["data"]
        
        # 6. 캐시 히트 시뮬레이션
        mock_redis_client.get.return_value = json.dumps(stock_data)
        response = client.get("/api/stocks/WORKFLOW001")
        assert response.status_code == 200
        
        # 7. 가격 데이터 조회 (캐시 미스)
        mock_redis_client.get.return_value = None
        response = client.get("/api/prices/WORKFLOW001")
        assert response.status_code == 200
        price_data = response.json()["data"]
        assert price_data["total"] == 1
        
        # 8. 날짜 범위로 가격 데이터 조회
        response = client.get("/api/prices/WORKFLOW001?start_date=2025-01-01&end_date=2025-01-01")
        assert response.status_code == 200
        assert response.json()["data"]["total"] == 1

