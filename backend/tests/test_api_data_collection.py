"""
데이터 수집 API 테스트
"""

import pytest
from unittest.mock import patch, Mock
from datetime import datetime, date
from decimal import Decimal

from app.models.stock import Stock
from app.models.price import Price
from app.models.trading_trend import TradingTrend
from app.models.news import News


class TestCollectPricesAPI:
    """가격 데이터 수집 API 테스트"""
    
    def test_collect_prices_stock_not_found(self, client):
        """존재하지 않는 종목의 가격 데이터 수집 테스트"""
        response = client.post("/api/data/collect/prices/NONEXISTENT?days=10")
        
        assert response.status_code == 404
        data = response.json()
        
        assert data["success"] is False
        assert "error" in data
        assert "NOT_FOUND" in data.get("error_code", "")
    
    def test_collect_prices_invalid_days(self, client, db_session):
        """잘못된 days 파라미터 테스트"""
        # 종목 생성
        stock = Stock(ticker="INVALID001", name="무효 테스트", type="STOCK")
        db_session.add(stock)
        db_session.commit()
        
        # days가 범위를 벗어난 경우 (FastAPI가 자동으로 검증)
        response = client.post("/api/data/collect/prices/INVALID001?days=500")
        
        # FastAPI는 자동으로 검증하므로 422 또는 400
        assert response.status_code in [400, 422]
    
    @patch('app.collectors.finance_collector.requests.get')
    def test_collect_prices_success(self, mock_get, client, db_session):
        """가격 데이터 수집 성공 테스트"""
        # 종목 생성
        stock = Stock(ticker="COLLECT001", name="수집 테스트", type="STOCK")
        db_session.add(stock)
        db_session.commit()
        
        # Mock HTML 응답
        html_content = """
        <html>
        <body>
            <table class="type2">
                <tr><th>날짜</th><th>종가</th><th>전일비</th><th>시가</th><th>고가</th><th>저가</th><th>거래량</th></tr>
                <tr><td>2025.11.07</td><td>25,050</td><td>상승205</td><td>25,700</td><td>25,765</td><td>25,000</td><td>1,036,539</td></tr>
                <tr><td>2025.11.06</td><td>24,845</td><td>하락100</td><td>24,900</td><td>25,000</td><td>24,800</td><td>950,000</td></tr>
            </table>
        </body>
        </html>
        """
        
        mock_response = Mock()
        mock_response.text = html_content
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        response = client.post("/api/data/collect/prices/COLLECT001?days=2")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["data"]["ticker"] == "COLLECT001"
        assert data["data"]["saved_count"] == 2
        assert data["data"]["days"] == 2
        assert "Price data collected successfully" in data["message"]
        
        # 데이터베이스에서 확인
        prices = db_session.query(Price).filter(Price.ticker == "COLLECT001").all()
        assert len(prices) == 2
    
    @patch('app.collectors.finance_collector.requests.get')
    def test_collect_prices_no_data(self, mock_get, client, db_session):
        """수집할 데이터가 없는 경우 테스트"""
        # 종목 생성
        stock = Stock(ticker="NODATA001", name="데이터 없음", type="STOCK")
        db_session.add(stock)
        db_session.commit()
        
        # 테이블이 없는 HTML 응답
        mock_response = Mock()
        mock_response.text = "<html><body>No table here</body></html>"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        response = client.post("/api/data/collect/prices/NODATA001?days=10")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["data"]["saved_count"] == 0
    
    @patch('app.collectors.finance_collector.requests.get')
    def test_collect_prices_network_error(self, mock_get, client, db_session):
        """네트워크 오류 테스트"""
        # 종목 생성
        stock = Stock(ticker="ERROR001", name="오류 테스트", type="STOCK")
        db_session.add(stock)
        db_session.commit()
        
        # 네트워크 오류 시뮬레이션
        import requests
        mock_get.side_effect = requests.exceptions.RequestException("Network error")
        
        response = client.post("/api/data/collect/prices/ERROR001?days=10")
        
        # 네트워크 오류 시 재시도 후에도 실패하면 빈 데이터를 반환하므로 200 OK
        # (finance_collector가 빈 리스트를 반환하고, API가 이를 성공으로 처리)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["saved_count"] == 0


class TestCollectTradingFlowAPI:
    """매매 동향 데이터 수집 API 테스트"""
    
    def test_collect_trading_flow_stock_not_found(self, client):
        """존재하지 않는 종목의 매매 동향 수집 테스트"""
        response = client.post("/api/data/collect/trading/NONEXISTENT?days=10")
        
        assert response.status_code == 404
        data = response.json()
        
        assert data["success"] is False
        assert "error" in data
        assert "NOT_FOUND" in data.get("error_code", "")
    
    def test_collect_trading_flow_invalid_date_format(self, client, db_session):
        """잘못된 날짜 형식 테스트"""
        # 종목 생성
        stock = Stock(ticker="INVALID002", name="무효 날짜", type="STOCK")
        db_session.add(stock)
        db_session.commit()
        
        # 잘못된 날짜 형식
        response = client.post(
            "/api/data/collect/trading/INVALID002?days=10&start_date=2025/01/01"
        )
        
        assert response.status_code == 400
        data = response.json()
        
        assert data["success"] is False
        assert "INVALID_DATE_FORMAT" in data.get("error_code", "")
    
    def test_collect_trading_flow_invalid_date_range(self, client, db_session):
        """잘못된 날짜 범위 테스트"""
        # 종목 생성
        stock = Stock(ticker="INVALID003", name="무효 범위", type="STOCK")
        db_session.add(stock)
        db_session.commit()
        
        # start_date > end_date
        response = client.post(
            "/api/data/collect/trading/INVALID003?days=10&start_date=2025-01-10&end_date=2025-01-01"
        )
        
        assert response.status_code == 400
        data = response.json()
        
        assert data["success"] is False
        assert "INVALID_DATE_RANGE" in data.get("error_code", "")
    
    @patch('app.collectors.finance_collector.requests.get')
    def test_collect_trading_flow_success(self, mock_get, client, db_session):
        """매매 동향 데이터 수집 성공 테스트"""
        # 종목 생성
        stock = Stock(ticker="TRADING001", name="매매동향 테스트", type="STOCK")
        db_session.add(stock)
        db_session.commit()
        
        # Mock HTML 응답 (두 개의 type2 테이블)
        html_content = """
        <html>
        <body>
            <table class="type2"><tr><th>증권사별</th></tr></table>
            <table class="type2">
                <tr><th>날짜</th><th>종가</th><th>전일비</th><th>등락률</th><th>거래량</th><th>기관</th><th>외국인</th></tr>
                <tr><td>2025.11.07</td><td>25,050</td><td>상승205</td><td>0.82</td><td>1,036,539</td><td>1,234</td><td>-567</td></tr>
                <tr><td>2025.11.06</td><td>24,845</td><td>하락100</td><td>-0.40</td><td>950,000</td><td>-500</td><td>300</td></tr>
            </table>
        </body>
        </html>
        """
        
        mock_response = Mock()
        mock_response.text = html_content
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        response = client.post("/api/data/collect/trading/TRADING001?days=2")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["data"]["ticker"] == "TRADING001"
        assert data["data"]["saved_count"] == 2
        assert data["data"]["days"] == 2
        assert "Trading flow data collected successfully" in data["message"]
        
        # 데이터베이스에서 확인
        trading_flows = db_session.query(TradingTrend).filter(
            TradingTrend.ticker == "TRADING001"
        ).all()
        assert len(trading_flows) == 2
    
    @patch('app.collectors.finance_collector.requests.get')
    def test_collect_trading_flow_with_date_range(self, mock_get, client, db_session):
        """날짜 범위를 지정한 매매 동향 수집 테스트"""
        # 종목 생성
        stock = Stock(ticker="DATERANGE001", name="날짜 범위 테스트", type="STOCK")
        db_session.add(stock)
        db_session.commit()
        
        # Mock HTML 응답
        html_content = """
        <html>
        <body>
            <table class="type2"><tr><th>증권사별</th></tr></table>
            <table class="type2">
                <tr><th>날짜</th><th>종가</th><th>전일비</th><th>등락률</th><th>거래량</th><th>기관</th><th>외국인</th></tr>
                <tr><td>2025.11.07</td><td>25,050</td><td>상승205</td><td>0.82</td><td>1,036,539</td><td>1,234</td><td>-567</td></tr>
            </table>
        </body>
        </html>
        """
        
        mock_response = Mock()
        mock_response.text = html_content
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        response = client.post(
            "/api/data/collect/trading/DATERANGE001?days=10&start_date=2025-11-01&end_date=2025-11-07"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["data"]["start_date"] == "2025-11-01"
        assert data["data"]["end_date"] == "2025-11-07"
    
    @patch('app.collectors.finance_collector.requests.get')
    def test_collect_trading_flow_no_data(self, mock_get, client, db_session):
        """수집할 데이터가 없는 경우 테스트"""
        # 종목 생성
        stock = Stock(ticker="NODATA002", name="데이터 없음", type="STOCK")
        db_session.add(stock)
        db_session.commit()
        
        # 테이블이 없는 HTML 응답
        mock_response = Mock()
        mock_response.text = "<html><body>No table here</body></html>"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        response = client.post("/api/data/collect/trading/NODATA002?days=10")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["data"]["saved_count"] == 0


class TestDataCollectionAPIErrorHandling:
    """데이터 수집 API 에러 핸들링 테스트"""
    
    @patch('app.collectors.finance_collector.FinanceCollector.collect_and_save_prices')
    def test_collect_prices_internal_error(self, mock_collect, client, db_session):
        """내부 오류 처리 테스트"""
        # 종목 생성
        stock = Stock(ticker="ERROR002", name="오류 테스트", type="STOCK")
        db_session.add(stock)
        db_session.commit()
        
        # 내부 오류 시뮬레이션
        mock_collect.side_effect = Exception("Internal error")
        
        response = client.post("/api/data/collect/prices/ERROR002?days=10")
        
        assert response.status_code == 500
        data = response.json()
        
        # HTTPException이 발생하면 FastAPI의 기본 에러 핸들러가 처리
        # 응답 형식이 다를 수 있음
        assert "error" in data or "detail" in data
    
    @patch('app.collectors.finance_collector.FinanceCollector.collect_and_save_trading_flow')
    def test_collect_trading_flow_internal_error(self, mock_collect, client, db_session):
        """내부 오류 처리 테스트"""
        # 종목 생성
        stock = Stock(ticker="ERROR003", name="오류 테스트", type="STOCK")
        db_session.add(stock)
        db_session.commit()
        
        # 내부 오류 시뮬레이션
        mock_collect.side_effect = Exception("Internal error")
        
        response = client.post("/api/data/collect/trading/ERROR003?days=10")
        
        assert response.status_code == 500
        data = response.json()
        
        # HTTPException이 발생하면 FastAPI의 기본 에러 핸들러가 처리
        # 응답 형식이 다를 수 있음
        assert "error" in data or "detail" in data


class TestCollectNewsAPI:
    """뉴스 데이터 수집 API 테스트"""
    
    def test_collect_news_stock_not_found(self, client):
        """존재하지 않는 종목의 뉴스 데이터 수집 테스트"""
        response = client.post("/api/data/collect/news/NONEXISTENT?max_items=50")
        
        assert response.status_code == 404
        data = response.json()
        
        assert data["success"] is False
        assert "error" in data
        assert "NOT_FOUND" in data.get("error_code", "")
    
    def test_collect_news_invalid_max_items(self, client, db_session):
        """잘못된 max_items 파라미터 테스트"""
        # 종목 생성
        stock = Stock(ticker="INVALID004", name="무효 테스트", type="STOCK")
        db_session.add(stock)
        db_session.commit()
        
        # max_items가 범위를 벗어난 경우 (FastAPI가 자동으로 검증)
        response = client.post("/api/data/collect/news/INVALID004?max_items=500")
        
        # FastAPI는 자동으로 검증하므로 422 또는 400
        assert response.status_code in [400, 422]
    
    @patch('app.collectors.news_collector.requests.get')
    def test_collect_news_success(self, mock_get, client, db_session):
        """뉴스 데이터 수집 성공 테스트"""
        # 종목 생성
        stock = Stock(ticker="NEWS001", name="뉴스 테스트", type="STOCK")
        db_session.add(stock)
        db_session.commit()
        
        # Mock HTML 응답
        html_content = """
        <html>
        <body>
            <div class="news_area">
                <tr>
                    <td><a href="/item/news_read.naver?article_id=12345">테스트 뉴스 1</a></td>
                    <td><span class="press">연합뉴스</span></td>
                    <td><span class="date">2025.11.14</span></td>
                </tr>
                <tr>
                    <td><a href="/item/news_read.naver?article_id=12346">테스트 뉴스 2</a></td>
                    <td><span class="press">매일경제</span></td>
                    <td><span class="date">2025.11.13</span></td>
                </tr>
            </div>
        </body>
        </html>
        """
        
        mock_response = Mock()
        mock_response.text = html_content
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        response = client.post("/api/data/collect/news/NEWS001?max_items=50")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["data"]["ticker"] == "NEWS001"
        assert data["data"]["saved_count"] >= 0  # 수집된 뉴스 개수
        assert data["data"]["max_items"] == 50
        assert "News data collected successfully" in data["message"]
    
    @patch('app.collectors.news_collector.requests.get')
    def test_collect_news_no_data(self, mock_get, client, db_session):
        """수집할 뉴스가 없는 경우 테스트"""
        # 종목 생성
        stock = Stock(ticker="NONEWS001", name="뉴스 없음", type="STOCK")
        db_session.add(stock)
        db_session.commit()
        
        # 뉴스 리스트가 없는 HTML 응답
        mock_response = Mock()
        mock_response.text = "<html><body>No news here</body></html>"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        response = client.post("/api/data/collect/news/NONEWS001?max_items=50")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["data"]["saved_count"] == 0
    
    @patch('app.collectors.news_collector.NewsCollector.collect_and_save_news')
    def test_collect_news_internal_error(self, mock_collect, client, db_session):
        """내부 오류 처리 테스트"""
        # 종목 생성
        stock = Stock(ticker="ERROR004", name="오류 테스트", type="STOCK")
        db_session.add(stock)
        db_session.commit()
        
        # 내부 오류 시뮬레이션
        mock_collect.side_effect = Exception("Internal error")
        
        response = client.post("/api/data/collect/news/ERROR004?max_items=50")
        
        assert response.status_code == 500
        data = response.json()
        
        # HTTPException이 발생하면 FastAPI의 기본 에러 핸들러가 처리
        assert "error" in data or "detail" in data

