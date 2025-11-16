"""
Finance 수집기 단위 테스트
"""

import pytest
from unittest.mock import patch, Mock, MagicMock
from datetime import date, datetime
from decimal import Decimal

from app.collectors.finance_collector import FinanceCollector
from app.models.stock import Stock
from app.models.price import Price
from app.models.trading_trend import TradingTrend


class TestFinanceCollectorInit:
    """FinanceCollector 초기화 테스트"""
    
    def test_init(self):
        """수집기 초기화 테스트"""
        collector = FinanceCollector()
        
        assert collector is not None
        assert 'User-Agent' in collector.headers
        assert collector.rate_limiter is not None


class TestFinanceCollectorParsing:
    """FinanceCollector 파싱 메서드 테스트"""
    
    @pytest.fixture
    def collector(self):
        """수집기 픽스처"""
        return FinanceCollector()
    
    def test_parse_number(self, collector):
        """숫자 파싱 테스트"""
        assert collector._parse_number("25,765") == 25765.0
        assert collector._parse_number("1,234,567") == 1234567.0
        assert collector._parse_number("") is None
        assert collector._parse_number("invalid") is None
        assert collector._parse_number(None) is None
        assert collector._parse_number("   ") is None
    
    def test_parse_change_positive(self, collector):
        """양수 등락률 파싱 테스트"""
        result = collector._parse_change("상승205", 25765.0)
        assert result is not None
        assert result > 0  # 상승
        assert round(result, 2) == 0.8
    
    def test_parse_change_negative(self, collector):
        """음수 등락률 파싱 테스트"""
        result = collector._parse_change("하락1,375", 25560.0)
        assert result is not None
        assert result < 0  # 하락
        assert abs(result) > 0
    
    def test_parse_change_zero(self, collector):
        """보합 등락률 파싱 테스트"""
        result = collector._parse_change("보합0", 25765.0)
        assert result == 0.0
    
    def test_parse_change_edge_cases(self, collector):
        """등락률 파싱 엣지 케이스 테스트"""
        # 빈 문자열
        assert collector._parse_change("", 10000.0) is None
        
        # None 입력
        assert collector._parse_change(None, 10000.0) is None
        
        # close_price가 0인 경우
        assert collector._parse_change("상승100", 0.0) is None
        
        # close_price가 None인 경우
        assert collector._parse_change("상승100", None) is None
    
    def test_parse_trading_volume(self, collector):
        """거래량 파싱 테스트"""
        assert collector._parse_trading_volume("1,234") == 1234
        assert collector._parse_trading_volume("-5,678") == -5678
        assert collector._parse_trading_volume("") is None
        assert collector._parse_trading_volume("-") is None
        assert collector._parse_trading_volume(None) is None


class TestFinanceCollectorValidation:
    """FinanceCollector 검증 메서드 테스트"""
    
    @pytest.fixture
    def collector(self):
        """수집기 픽스처"""
        return FinanceCollector()
    
    def test_clean_price_data(self, collector):
        """가격 데이터 정제 테스트"""
        data = {
            'ticker': '487240',
            'date': date(2025, 11, 7),
            'open_price': 25700.123456,
            'high_price': 25765.987654,
            'low_price': 25000.555555,
            'current_price': 25050.777777,
            'volume': 1036539.0,  # float
            'change_rate': -2.78123456
        }
        
        cleaned = collector.clean_price_data(data)
        
        assert cleaned['open_price'] == 25700.12
        assert cleaned['high_price'] == 25765.99
        assert cleaned['low_price'] == 25000.56
        assert cleaned['current_price'] == 25050.78
        assert cleaned['change_rate'] == -2.78
        assert isinstance(cleaned['volume'], int)
        assert cleaned['volume'] == 1036539
    
    def test_clean_price_data_none_volume(self, collector):
        """None 거래량 정제 테스트"""
        data = {
            'ticker': '487240',
            'date': date(2025, 11, 7),
            'current_price': 25050.0,
            'volume': None
        }
        
        cleaned = collector.clean_price_data(data)
        
        assert cleaned['volume'] == 0


class TestFinanceCollectorFetch:
    """FinanceCollector 데이터 수집 메서드 테스트"""
    
    @pytest.fixture
    def collector(self):
        """수집기 픽스처"""
        return FinanceCollector()
    
    @patch('app.collectors.finance_collector.requests.get')
    def test_fetch_naver_finance_prices_success(self, mock_get, collector):
        """가격 데이터 수집 성공 테스트"""
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
        
        data = collector.fetch_naver_finance_prices("487240", days=2)
        
        assert len(data) == 2
        assert data[0]['ticker'] == "487240"
        assert data[0]['date'] == date(2025, 11, 7)
        assert data[0]['current_price'] == 25050.0
        assert data[1]['date'] == date(2025, 11, 6)
    
    @patch('app.collectors.finance_collector.requests.get')
    def test_fetch_naver_finance_prices_table_not_found(self, mock_get, collector):
        """테이블을 찾을 수 없는 경우 테스트"""
        mock_response = Mock()
        mock_response.text = "<html><body>No table here</body></html>"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        data = collector.fetch_naver_finance_prices("487240", days=5)
        
        assert len(data) == 0
    
    @patch('app.collectors.finance_collector.requests.get')
    def test_fetch_naver_finance_prices_network_error(self, mock_get, collector):
        """네트워크 오류 테스트"""
        import requests
        mock_get.side_effect = requests.exceptions.RequestException("Network error")
        
        data = collector.fetch_naver_finance_prices("487240", days=5)
        
        # 재시도 후에도 실패하면 빈 리스트 반환
        assert len(data) == 0
    
    @patch('app.collectors.finance_collector.requests.get')
    def test_fetch_naver_trading_flow_success(self, mock_get, collector):
        """매매 동향 데이터 수집 성공 테스트"""
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
        
        data = collector.fetch_naver_trading_flow("487240", days=2)
        
        assert len(data) == 2
        assert data[0]['ticker'] == "487240"
        assert data[0]['date'] == date(2025, 11, 7)
        assert data[0]['institution'] == 1234
        assert data[0]['foreign_investor'] == -567
        # 개인 = -(기관 + 외국인)
        assert data[0]['individual'] == -(1234 + (-567))


class TestFinanceCollectorSave:
    """FinanceCollector 데이터 저장 메서드 테스트"""
    
    @pytest.fixture
    def collector(self):
        """수집기 픽스처"""
        return FinanceCollector()
    
    def test_save_price_data_empty(self, collector, db_session):
        """빈 가격 데이터 저장 테스트"""
        saved_count = collector.save_price_data(db_session, [])
        assert saved_count == 0
    
    def test_save_price_data_valid(self, collector, db_session):
        """유효한 가격 데이터 저장 테스트"""
        # 종목 생성
        stock = Stock(ticker="SAVE001", name="저장 테스트", type="STOCK")
        db_session.add(stock)
        db_session.commit()
        
        # 가격 데이터
        price_data = [{
            'ticker': "SAVE001",
            'date': date(2025, 11, 7),
            'timestamp': datetime.now(),
            'current_price': 25050.0,
            'open_price': 25700.0,
            'high_price': 25765.0,
            'low_price': 25000.0,
            'volume': 1036539,
            'change_rate': 0.8,
            'change_amount': 205.0
        }]
        
        saved_count = collector.save_price_data(db_session, price_data)
        assert saved_count == 1
        
        # 데이터베이스에서 확인
        saved_price = db_session.query(Price).filter(Price.ticker == "SAVE001").first()
        assert saved_price is not None
        assert float(saved_price.current_price) == 25050.0
    
    def test_save_price_data_invalid(self, collector, db_session):
        """유효하지 않은 가격 데이터 저장 테스트"""
        # 종목 생성
        stock = Stock(ticker="INVALID001", name="무효 테스트", type="STOCK")
        db_session.add(stock)
        db_session.commit()
        
        # 유효하지 않은 데이터 (음수 가격)
        price_data = [{
            'ticker': "INVALID001",
            'date': date(2025, 11, 7),
            'timestamp': datetime.now(),
            'current_price': -100.0,  # 음수 가격
            'volume': 1000
        }]
        
        saved_count = collector.save_price_data(db_session, price_data)
        assert saved_count == 0  # 검증 실패로 저장되지 않음
    
    def test_save_price_data_update_existing(self, collector, db_session):
        """기존 가격 데이터 업데이트 테스트"""
        # 종목 생성
        stock = Stock(ticker="UPDATE001", name="업데이트 테스트", type="STOCK")
        db_session.add(stock)
        db_session.commit()
        
        # 기존 가격 데이터
        existing_price = Price(
            ticker="UPDATE001",
            date=date(2025, 11, 7),
            timestamp=datetime(2025, 11, 7, 10, 0, 0),
            current_price=Decimal("25000.0")
        )
        db_session.add(existing_price)
        db_session.commit()
        
        # 업데이트할 데이터
        price_data = [{
            'ticker': "UPDATE001",
            'date': date(2025, 11, 7),
            'timestamp': datetime.now(),
            'current_price': 25050.0,
            'open_price': 25700.0,
            'high_price': 25765.0,
            'low_price': 25000.0,
            'volume': 1036539
        }]
        
        saved_count = collector.save_price_data(db_session, price_data)
        assert saved_count == 1
        
        # 업데이트 확인
        updated_price = db_session.query(Price).filter(
            Price.ticker == "UPDATE001",
            Price.date == date(2025, 11, 7)
        ).first()
        assert float(updated_price.current_price) == 25050.0
    
    def test_save_trading_flow_data_valid(self, collector, db_session):
        """유효한 매매 동향 데이터 저장 테스트"""
        # 종목 생성
        stock = Stock(ticker="TRADING001", name="매매동향 테스트", type="STOCK")
        db_session.add(stock)
        db_session.commit()
        
        # 매매 동향 데이터
        trading_data = [{
            'ticker': "TRADING001",
            'date': date(2025, 11, 7),
            'timestamp': datetime.now(),
            'individual': -667,
            'institution': 1234,
            'foreign_investor': -567,
            'total': 2468
        }]
        
        saved_count = collector.save_trading_flow_data(db_session, trading_data)
        assert saved_count == 1
        
        # 데이터베이스에서 확인
        saved_trading = db_session.query(TradingTrend).filter(
            TradingTrend.ticker == "TRADING001"
        ).first()
        assert saved_trading is not None
        assert int(saved_trading.individual) == -667
        assert int(saved_trading.institution) == 1234
    
    def test_save_trading_flow_data_invalid(self, collector, db_session):
        """유효하지 않은 매매 동향 데이터 저장 테스트"""
        # 종목 생성
        stock = Stock(ticker="INVALID002", name="무효 매매동향", type="STOCK")
        db_session.add(stock)
        db_session.commit()
        
        # 유효하지 않은 데이터 (필수 필드 누락)
        trading_data = [{
            'ticker': "INVALID002",
            # 'date' 필드 누락
            'timestamp': datetime.now(),
            'individual': -667
        }]
        
        saved_count = collector.save_trading_flow_data(db_session, trading_data)
        assert saved_count == 0  # 검증 실패로 저장되지 않음


class TestFinanceCollectorIntegration:
    """FinanceCollector 통합 테스트"""
    
    @pytest.fixture
    def collector(self):
        """수집기 픽스처"""
        return FinanceCollector()
    
    @patch('app.collectors.finance_collector.requests.get')
    def test_collect_and_save_prices_integration(self, mock_get, collector, db_session):
        """가격 데이터 수집 및 저장 통합 테스트"""
        # 종목 생성
        stock = Stock(ticker="INTEG001", name="통합 테스트", type="STOCK")
        db_session.add(stock)
        db_session.commit()
        
        # Mock HTML 응답
        html_content = """
        <html>
        <body>
            <table class="type2">
                <tr><th>날짜</th><th>종가</th><th>전일비</th><th>시가</th><th>고가</th><th>저가</th><th>거래량</th></tr>
                <tr><td>2025.11.07</td><td>25,050</td><td>상승205</td><td>25,700</td><td>25,765</td><td>25,000</td><td>1,036,539</td></tr>
            </table>
        </body>
        </html>
        """
        
        mock_response = Mock()
        mock_response.text = html_content
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # 수집 및 저장
        saved_count = collector.collect_and_save_prices(db_session, "INTEG001", days=1)
        
        assert saved_count == 1
        
        # 데이터베이스에서 확인
        saved_price = db_session.query(Price).filter(Price.ticker == "INTEG001").first()
        assert saved_price is not None
        assert saved_price.date == date(2025, 11, 7)
        assert float(saved_price.current_price) == 25050.0



