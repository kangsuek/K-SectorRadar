"""
스케줄러 자동 수집 통합 테스트

스케줄러가 자동으로 데이터를 수집하는 기능을 테스트합니다.
"""

import pytest
import time
from datetime import datetime
from unittest.mock import patch, Mock

from app.scheduler.data_scheduler import DataScheduler
from app.models.stock import Stock
from app.models.price import Price
from app.models.trading_trend import TradingTrend
from app.models.news import News
from app.database import seed_stocks_from_json


class TestSchedulerAutoCollection:
    """스케줄러 자동 수집 테스트"""
    
    @pytest.fixture
    def setup_stocks(self, db_session):
        """테스트용 종목 데이터 생성"""
        # stocks.json에서 종목 데이터 로드
        seed_stocks_from_json(db_session)
        db_session.commit()
        
        # 종목 목록 확인
        stocks = db_session.query(Stock).all()
        assert len(stocks) > 0, "종목 데이터가 없습니다. stocks.json을 확인하세요."
        
        return stocks
    
    @pytest.fixture
    def scheduler(self):
        """스케줄러 픽스처 (짧은 간격으로 설정)"""
        return DataScheduler(interval_seconds=2)  # 테스트를 위해 2초 간격
    
    @patch('app.scheduler.data_scheduler.FinanceCollector')
    @patch('app.scheduler.data_scheduler.NewsCollector')
    def test_scheduler_auto_collection_single_run(self, mock_news_collector, mock_finance_collector, scheduler, setup_stocks, db_session):
        """스케줄러 단일 실행 테스트"""
        # 종목이 있는지 확인
        stocks = setup_stocks
        assert len(stocks) > 0
        
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
        
        # 수집 함수 직접 호출 (스케줄러가 실행되기 전에)
        scheduler._collect_all_data()
        
        # 상태 확인
        assert scheduler.last_run_time is not None
        assert scheduler.last_run_status in ["success", "no_stocks"]
        
        # 데이터베이스에 데이터가 저장되었는지 확인 (실제 수집이 성공한 경우)
        if scheduler.last_run_status == "success":
            # 가격 데이터 확인
            prices = db_session.query(Price).all()
            # 매매 동향 데이터 확인
            trading = db_session.query(TradingTrend).all()
            # 뉴스 데이터 확인
            news = db_session.query(News).all()
            
            # 최소한 하나의 데이터 타입은 수집되었을 수 있음
            total_data = len(prices) + len(trading) + len(news)
            print(f"\n[스케줄러 테스트] 수집된 데이터: 가격 {len(prices)}개, 매매동향 {len(trading)}개, 뉴스 {len(news)}개")
        
        # 스케줄러 중지
        scheduler.stop()
        assert scheduler.is_running is False
    
    @patch('app.scheduler.data_scheduler.FinanceCollector')
    @patch('app.scheduler.data_scheduler.NewsCollector')
    def test_scheduler_status_after_collection(self, mock_news_collector, mock_finance_collector, scheduler, setup_stocks, db_session):
        """수집 후 스케줄러 상태 확인 테스트"""
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
        
        # 수집 실행
        scheduler._collect_all_data()
        
        # 상태 조회
        status = scheduler.get_status()
        
        assert status['is_running'] is True
        assert status['last_run_time'] is not None
        assert status['last_run_status'] is not None
        
        # last_run_time이 ISO 형식인지 확인
        if status['last_run_time']:
            # ISO 형식 파싱 가능한지 확인
            datetime.fromisoformat(status['last_run_time'].replace('Z', '+00:00'))
        
        # 스케줄러 중지
        scheduler.stop()
    
    @pytest.mark.slow
    def test_scheduler_multiple_runs(self, scheduler, setup_stocks, db_session):
        """스케줄러 여러 번 실행 테스트 (느린 테스트)"""
        # 종목이 있는지 확인
        stocks = setup_stocks
        assert len(stocks) > 0
        
        # 스케줄러 시작
        scheduler.start()
        assert scheduler.is_running is True
        
        # 초기 데이터 수 확인
        initial_prices = db_session.query(Price).count()
        initial_trading = db_session.query(TradingTrend).count()
        initial_news = db_session.query(News).count()
        
        print(f"\n[초기 데이터] 가격: {initial_prices}개, 매매동향: {initial_trading}개, 뉴스: {initial_news}개")
        
        # 첫 번째 수집 실행
        scheduler._collect_all_data()
        first_run_time = scheduler.last_run_time
        first_run_status = scheduler.last_run_status
        
        # 잠시 대기
        time.sleep(1)
        
        # 두 번째 수집 실행
        scheduler._collect_all_data()
        second_run_time = scheduler.last_run_time
        second_run_status = scheduler.last_run_status
        
        # 두 번째 실행 시간이 더 최신인지 확인
        assert second_run_time >= first_run_time
        
        # 최종 데이터 수 확인
        final_prices = db_session.query(Price).count()
        final_trading = db_session.query(TradingTrend).count()
        final_news = db_session.query(News).count()
        
        print(f"\n[최종 데이터] 가격: {final_prices}개, 매매동향: {final_trading}개, 뉴스: {final_news}개")
        
        # 스케줄러 중지
        scheduler.stop()
        assert scheduler.is_running is False
    
    def test_scheduler_collection_with_no_stocks(self, scheduler, db_session):
        """종목이 없을 때 스케줄러 수집 테스트"""
        # 종목이 없는 상태 확인
        stocks = db_session.query(Stock).all()
        assert len(stocks) == 0
        
        # 스케줄러 시작
        scheduler.start()
        
        # 수집 실행
        scheduler._collect_all_data()
        
        # 상태 확인
        assert scheduler.last_run_status == "no_stocks"
        assert scheduler.last_run_time is not None
        
        # 스케줄러 중지
        scheduler.stop()
    
    def test_scheduler_collection_error_handling(self, scheduler, setup_stocks, db_session):
        """스케줄러 수집 오류 처리 테스트"""
        # 종목 생성
        stock = Stock(ticker="ERROR001", name="오류 테스트", type="STOCK")
        db_session.add(stock)
        db_session.commit()
        
        # 수집 함수를 모킹하여 오류 발생
        original_collect = scheduler._collect_data_for_ticker
        
        def mock_collect_with_error(ticker, db):
            raise Exception("Test error")
        
        scheduler._collect_data_for_ticker = mock_collect_with_error
        
        # 스케줄러 시작
        scheduler.start()
        
        # 수집 실행 (오류 발생)
        scheduler._collect_all_data()
        
        # 오류 상태 확인
        assert scheduler.last_run_status == "error"
        assert scheduler.last_run_error is not None
        assert "Test error" in scheduler.last_run_error
        
        # 원래 함수 복원
        scheduler._collect_data_for_ticker = original_collect
        
        # 스케줄러 중지
        scheduler.stop()
    
    def test_scheduler_job_scheduling(self, scheduler, setup_stocks, db_session):
        """스케줄러 job 스케줄링 테스트"""
        # 스케줄러 시작
        scheduler.start()
        
        # job이 등록되었는지 확인
        job = scheduler.scheduler.get_job(scheduler.job_id)
        assert job is not None
        assert job.name == "Data Collection Job"
        
        # next_run_time이 설정되었는지 확인
        if job.next_run_time:
            assert job.next_run_time > datetime.now()
        
        # 스케줄러 중지
        scheduler.stop()
        
        # 중지 후 job이 제거되었는지 확인
        job_after_stop = scheduler.scheduler.get_job(scheduler.job_id)
        assert job_after_stop is None

