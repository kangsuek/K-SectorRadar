"""
DataScheduler 단위 테스트
"""

import pytest
from unittest.mock import patch, Mock, MagicMock
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

from app.scheduler.data_scheduler import DataScheduler, get_scheduler
from app.models.stock import Stock
from app.models.price import Price
from app.models.trading_trend import TradingTrend
from app.models.news import News


class TestDataSchedulerInit:
    """DataScheduler 초기화 테스트"""
    
    def test_init_default_interval(self):
        """기본 간격으로 초기화 테스트"""
        scheduler = DataScheduler()
        
        assert scheduler is not None
        assert scheduler.interval_seconds == 30  # 기본값
        assert scheduler.is_running is False
        assert scheduler.scheduler is not None
        assert isinstance(scheduler.scheduler, BackgroundScheduler)
    
    def test_init_custom_interval(self):
        """커스텀 간격으로 초기화 테스트"""
        scheduler = DataScheduler(interval_seconds=60)
        
        assert scheduler.interval_seconds == 60
        assert scheduler.is_running is False
    
    def test_get_scheduler_singleton(self):
        """싱글톤 패턴 테스트"""
        scheduler1 = get_scheduler()
        scheduler2 = get_scheduler()
        
        assert scheduler1 is scheduler2


class TestDataSchedulerTickerManagement:
    """DataScheduler 종목 관리 메서드 테스트"""
    
    @pytest.fixture
    def scheduler(self):
        """스케줄러 픽스처"""
        return DataScheduler()
    
    def test_get_all_tickers(self, scheduler, db_session):
        """모든 종목 코드 조회 테스트"""
        # 종목 생성
        stock1 = Stock(ticker="TICKER001", name="종목 1", type="STOCK")
        stock2 = Stock(ticker="TICKER002", name="종목 2", type="STOCK")
        db_session.add(stock1)
        db_session.add(stock2)
        db_session.commit()
        
        tickers = scheduler._get_all_tickers(db_session)
        
        assert len(tickers) == 2
        assert "TICKER001" in tickers
        assert "TICKER002" in tickers
    
    def test_get_all_tickers_empty(self, scheduler, db_session):
        """종목이 없는 경우 테스트"""
        tickers = scheduler._get_all_tickers(db_session)
        
        assert len(tickers) == 0
        assert isinstance(tickers, list)


class TestDataSchedulerDataCollection:
    """DataScheduler 데이터 수집 메서드 테스트"""
    
    @pytest.fixture
    def scheduler(self):
        """스케줄러 픽스처"""
        return DataScheduler()
    
    @patch('app.scheduler.data_scheduler.FinanceCollector')
    @patch('app.scheduler.data_scheduler.NewsCollector')
    def test_collect_data_for_ticker_success(self, mock_news_collector, mock_finance_collector, scheduler, db_session):
        """종목별 데이터 수집 성공 테스트"""
        # 종목 생성
        stock = Stock(ticker="COLLECT001", name="수집 테스트", type="STOCK")
        db_session.add(stock)
        db_session.commit()
        
        # Mock 수집기 설정
        mock_finance = Mock()
        mock_finance.collect_and_save_prices.return_value = 5
        mock_finance.collect_and_save_trading_flow.return_value = 5
        mock_finance_collector.return_value = mock_finance
        
        mock_news = Mock()
        mock_news.collect_and_save_news.return_value = 10
        mock_news_collector.return_value = mock_news
        
        result = scheduler._collect_data_for_ticker("COLLECT001", db_session)
        
        assert result['ticker'] == "COLLECT001"
        assert result['prices_count'] == 5
        assert result['trading_count'] == 5
        assert result['news_count'] == 10
        assert len(result['errors']) == 0
    
    @patch('app.scheduler.data_scheduler.FinanceCollector')
    @patch('app.scheduler.data_scheduler.NewsCollector')
    def test_collect_data_for_ticker_with_error(self, mock_news_collector, mock_finance_collector, scheduler, db_session):
        """종목별 데이터 수집 오류 테스트"""
        # 종목 생성
        stock = Stock(ticker="ERROR001", name="오류 테스트", type="STOCK")
        db_session.add(stock)
        db_session.commit()
        
        # Mock 수집기에서 예외 발생
        mock_finance = Mock()
        mock_finance.collect_and_save_prices.side_effect = Exception("Collection error")
        mock_finance_collector.return_value = mock_finance
        
        result = scheduler._collect_data_for_ticker("ERROR001", db_session)
        
        assert result['ticker'] == "ERROR001"
        assert len(result['errors']) > 0
        assert "Collection error" in result['errors'][0]
    
    @patch('app.scheduler.data_scheduler.FinanceCollector')
    @patch('app.scheduler.data_scheduler.NewsCollector')
    @patch('app.scheduler.data_scheduler.SessionLocal')
    def test_collect_all_data_success(self, mock_session_local, mock_news_collector, mock_finance_collector, scheduler, db_session):
        """전체 데이터 수집 성공 테스트"""
        # 종목 생성
        stock1 = Stock(ticker="ALL001", name="전체 수집 1", type="STOCK")
        stock2 = Stock(ticker="ALL002", name="전체 수집 2", type="STOCK")
        db_session.add(stock1)
        db_session.add(stock2)
        db_session.commit()
        
        # Mock 세션 로컬
        mock_session_local.return_value = db_session
        
        # Mock 수집기 설정
        mock_finance = Mock()
        mock_finance.collect_and_save_prices.return_value = 3
        mock_finance.collect_and_save_trading_flow.return_value = 3
        mock_finance_collector.return_value = mock_finance
        
        mock_news = Mock()
        mock_news.collect_and_save_news.return_value = 5
        mock_news_collector.return_value = mock_news
        
        # 전체 데이터 수집 실행
        scheduler._collect_all_data()
        
        # 상태 확인
        assert scheduler.last_run_time is not None
        assert scheduler.last_run_status == "success"
    
    @patch('app.scheduler.data_scheduler.SessionLocal')
    def test_collect_all_data_no_stocks(self, mock_session_local, scheduler, db_session):
        """종목이 없는 경우 테스트"""
        # Mock 세션 로컬
        mock_session_local.return_value = db_session
        
        # 전체 데이터 수집 실행
        scheduler._collect_all_data()
        
        # 상태 확인
        assert scheduler.last_run_status == "no_stocks"
    
    @patch('app.scheduler.data_scheduler.SessionLocal')
    @patch('app.scheduler.data_scheduler.FinanceCollector')
    def test_collect_all_data_with_error(self, mock_finance_collector, mock_session_local, scheduler, db_session):
        """전체 데이터 수집 오류 테스트 (개별 종목 오류는 전체를 실패로 처리하지 않음)"""
        # 종목 생성
        stock = Stock(ticker="ERROR002", name="오류 테스트 2", type="STOCK")
        db_session.add(stock)
        db_session.commit()
        
        # Mock 세션 로컬
        mock_session_local.return_value = db_session
        
        # Mock 수집기에서 예외 발생
        mock_finance = Mock()
        mock_finance.collect_and_save_prices.side_effect = Exception("Database error")
        mock_finance_collector.return_value = mock_finance
        
        # 전체 데이터 수집 실행
        scheduler._collect_all_data()
        
        # 상태 확인: 개별 종목 오류는 전체를 실패로 처리하지 않고 성공으로 처리됨
        # 하지만 오류는 result['errors']에 포함됨
        assert scheduler.last_run_status == "success"  # 개별 오류는 전체를 실패로 처리하지 않음
        # 오류는 로그에 기록되지만 전체 상태는 성공


class TestDataSchedulerControl:
    """DataScheduler 제어 메서드 테스트"""
    
    @pytest.fixture
    def scheduler(self):
        """스케줄러 픽스처"""
        return DataScheduler()
    
    def test_start(self, scheduler):
        """스케줄러 시작 테스트"""
        assert scheduler.is_running is False
        
        scheduler.start()
        
        assert scheduler.is_running is True
        assert scheduler.scheduler.running is True
        
        # 정리
        scheduler.stop()
    
    def test_start_already_running(self, scheduler):
        """이미 실행 중인 스케줄러 시작 테스트"""
        scheduler.start()
        assert scheduler.is_running is True
        
        # 다시 시작 시도 (경고만 발생)
        scheduler.start()
        assert scheduler.is_running is True
        
        # 정리
        scheduler.stop()
    
    def test_stop(self, scheduler):
        """스케줄러 중지 테스트"""
        scheduler.start()
        assert scheduler.is_running is True
        
        scheduler.stop()
        
        assert scheduler.is_running is False
    
    def test_stop_not_running(self, scheduler):
        """실행 중이 아닌 스케줄러 중지 테스트"""
        assert scheduler.is_running is False
        
        # 중지 시도 (경고만 발생)
        scheduler.stop()
        
        assert scheduler.is_running is False
    
    def test_shutdown(self, scheduler):
        """스케줄러 종료 테스트"""
        scheduler.start()
        assert scheduler.is_running is True
        
        scheduler.shutdown()
        
        assert scheduler.is_running is False
    
    def test_get_status_not_running(self, scheduler):
        """실행 중이 아닐 때 상태 조회 테스트"""
        status = scheduler.get_status()
        
        assert status['is_running'] is False
        assert status['interval_seconds'] == 30
        assert status['next_run_time'] is None
        assert status['last_run_time'] is None
        assert status['last_run_status'] is None
        assert status['last_run_error'] is None
    
    def test_get_status_running(self, scheduler):
        """실행 중일 때 상태 조회 테스트"""
        scheduler.start()
        
        status = scheduler.get_status()
        
        assert status['is_running'] is True
        assert status['interval_seconds'] == 30
        # next_run_time은 스케줄러가 실행 중일 때만 설정됨
        
        # 정리
        scheduler.stop()
    
    def test_get_status_after_run(self, scheduler):
        """실행 후 상태 조회 테스트"""
        scheduler.last_run_time = datetime(2025, 11, 14, 10, 0, 0)
        scheduler.last_run_status = "success"
        scheduler.last_run_error = None
        
        status = scheduler.get_status()
        
        assert status['last_run_time'] == "2025-11-14T10:00:00"
        assert status['last_run_status'] == "success"
        assert status['last_run_error'] is None


class TestDataSchedulerIntegration:
    """DataScheduler 통합 테스트"""
    
    @pytest.fixture
    def scheduler(self):
        """스케줄러 픽스처"""
        return DataScheduler(interval_seconds=1)  # 테스트를 위해 짧은 간격
    
    @patch('app.scheduler.data_scheduler.FinanceCollector')
    @patch('app.scheduler.data_scheduler.NewsCollector')
    @patch('app.scheduler.data_scheduler.SessionLocal')
    def test_scheduler_lifecycle(self, mock_session_local, mock_news_collector, mock_finance_collector, scheduler, db_session):
        """스케줄러 생명주기 테스트"""
        # 종목 생성
        stock = Stock(ticker="LIFECYCLE001", name="생명주기 테스트", type="STOCK")
        db_session.add(stock)
        db_session.commit()
        
        # Mock 세션 로컬
        mock_session_local.return_value = db_session
        
        # Mock 수집기 설정
        mock_finance = Mock()
        mock_finance.collect_and_save_prices.return_value = 1
        mock_finance.collect_and_save_trading_flow.return_value = 1
        mock_finance_collector.return_value = mock_finance
        
        mock_news = Mock()
        mock_news.collect_and_save_news.return_value = 1
        mock_news_collector.return_value = mock_news
        
        # 스케줄러 시작
        scheduler.start()
        assert scheduler.is_running is True
        
        # 잠시 대기 (실제로는 스케줄러가 실행되지만, 테스트에서는 즉시 확인)
        import time
        time.sleep(0.1)  # 100ms 대기
        
        # 스케줄러 중지
        scheduler.stop()
        assert scheduler.is_running is False

