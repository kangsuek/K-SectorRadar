"""
데이터 수집 스케줄러

APScheduler를 사용하여 주기적으로 데이터를 수집합니다.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging
import atexit

from app.database import SessionLocal
from app.models.stock import Stock
from app.collectors.finance_collector import FinanceCollector
from app.collectors.news_collector import NewsCollector

logger = logging.getLogger(__name__)

# 기본 수집 간격 (30초)
DEFAULT_COLLECTION_INTERVAL = 30


class DataScheduler:
    """데이터 수집 스케줄러"""
    
    def __init__(self, interval_seconds: int = DEFAULT_COLLECTION_INTERVAL):
        """
        스케줄러 초기화
        
        Args:
            interval_seconds: 데이터 수집 간격 (초 단위, 기본: 30초)
        """
        self.scheduler = BackgroundScheduler()
        self.interval_seconds = interval_seconds
        self.is_running = False
        self.job_id = "data_collection_job"
        self.last_run_time: Optional[datetime] = None
        self.last_run_status: Optional[str] = None
        self.last_run_error: Optional[str] = None
        
        # 종료 시 스케줄러 정리
        atexit.register(self.shutdown)
    
    def _get_all_tickers(self, db: Session) -> List[str]:
        """
        데이터베이스에서 모든 종목 코드 조회
        
        Args:
            db: 데이터베이스 세션
        
        Returns:
            종목 코드 리스트
        """
        stocks = db.query(Stock).all()
        return [stock.ticker for stock in stocks]
    
    def _collect_data_for_ticker(self, ticker: str, db: Session) -> dict:
        """
        특정 종목에 대한 데이터 수집
        
        Args:
            ticker: 종목 코드
            db: 데이터베이스 세션
        
        Returns:
            수집 결과 딕셔너리
        """
        result = {
            'ticker': ticker,
            'prices_count': 0,
            'trading_count': 0,
            'news_count': 0,
            'errors': []
        }
        
        try:
            # 가격 데이터 수집 (최근 10일)
            finance_collector = FinanceCollector()
            prices_count = finance_collector.collect_and_save_prices(db, ticker, days=10)
            result['prices_count'] = prices_count
            
            # 매매 동향 데이터 수집 (최근 10일)
            trading_count = finance_collector.collect_and_save_trading_flow(db, ticker, days=10)
            result['trading_count'] = trading_count
            
            # 뉴스 데이터 수집 (최근 50개)
            news_collector = NewsCollector()
            news_count = news_collector.collect_and_save_news(db, ticker, max_items=50)
            result['news_count'] = news_count
            
        except Exception as e:
            error_msg = f"Error collecting data for {ticker}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            result['errors'].append(error_msg)
        
        return result
    
    def _collect_all_data(self):
        """
        모든 종목에 대한 데이터 수집 (스케줄러에서 호출)
        """
        logger.info("Starting scheduled data collection")
        self.last_run_time = datetime.now()
        
        db: Session = SessionLocal()
        try:
            # 모든 종목 코드 조회
            tickers = self._get_all_tickers(db)
            
            if not tickers:
                logger.warning("No stocks found in database")
                self.last_run_status = "no_stocks"
                return
            
            logger.info(f"Collecting data for {len(tickers)} stocks")
            
            total_results = {
                'total_tickers': len(tickers),
                'successful': 0,
                'failed': 0,
                'total_prices': 0,
                'total_trading': 0,
                'total_news': 0,
                'errors': []
            }
            
            # 각 종목에 대해 데이터 수집
            for ticker in tickers:
                try:
                    result = self._collect_data_for_ticker(ticker, db)
                    
                    total_results['total_prices'] += result['prices_count']
                    total_results['total_trading'] += result['trading_count']
                    total_results['total_news'] += result['news_count']
                    
                    if result['errors']:
                        total_results['failed'] += 1
                        total_results['errors'].extend(result['errors'])
                    else:
                        total_results['successful'] += 1
                    
                    # 트랜잭션 커밋 (각 종목마다)
                    db.commit()
                    
                except Exception as e:
                    db.rollback()
                    error_msg = f"Failed to collect data for {ticker}: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    total_results['failed'] += 1
                    total_results['errors'].append(error_msg)
            
            self.last_run_status = "success"
            logger.info(
                f"Data collection completed: {total_results['successful']} successful, "
                f"{total_results['failed']} failed, "
                f"{total_results['total_prices']} prices, "
                f"{total_results['total_trading']} trading, "
                f"{total_results['total_news']} news"
            )
            
        except Exception as e:
            db.rollback()
            error_msg = f"Error in scheduled data collection: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.last_run_status = "error"
            self.last_run_error = error_msg
        finally:
            db.close()
    
    def start(self):
        """
        스케줄러 시작
        """
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        try:
            # 기존 job이 있으면 제거
            if self.scheduler.get_job(self.job_id):
                self.scheduler.remove_job(self.job_id)
            
            # 스케줄러 시작
            self.scheduler.start()
            
            # 데이터 수집 job 추가 (30초 간격)
            trigger = IntervalTrigger(seconds=self.interval_seconds)
            self.scheduler.add_job(
                func=self._collect_all_data,
                trigger=trigger,
                id=self.job_id,
                name="Data Collection Job",
                replace_existing=True,
            )
            
            self.is_running = True
            logger.info(f"Scheduler started with {self.interval_seconds} second interval")
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}", exc_info=True)
            raise
    
    def stop(self):
        """
        스케줄러 중지
        """
        if not self.is_running:
            logger.warning("Scheduler is not running")
            return
        
        try:
            # job 제거
            if self.scheduler.get_job(self.job_id):
                self.scheduler.remove_job(self.job_id)
            
            # 스케줄러 중지
            self.scheduler.shutdown(wait=False)
            
            self.is_running = False
            logger.info("Scheduler stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop scheduler: {e}", exc_info=True)
            raise
    
    def shutdown(self):
        """
        스케줄러 종료 (atexit에서 호출)
        """
        if self.is_running:
            self.stop()
    
    def get_status(self) -> dict:
        """
        스케줄러 상태 조회
        
        Returns:
            스케줄러 상태 딕셔너리
        """
        job = self.scheduler.get_job(self.job_id) if self.scheduler.running else None
        
        return {
            'is_running': self.is_running,
            'interval_seconds': self.interval_seconds,
            'next_run_time': job.next_run_time.isoformat() if job and job.next_run_time else None,
            'last_run_time': self.last_run_time.isoformat() if self.last_run_time else None,
            'last_run_status': self.last_run_status,
            'last_run_error': self.last_run_error,
        }


# 전역 스케줄러 인스턴스
_scheduler_instance: Optional[DataScheduler] = None


def get_scheduler(interval_seconds: int = DEFAULT_COLLECTION_INTERVAL) -> DataScheduler:
    """
    전역 스케줄러 인스턴스 가져오기 (싱글톤 패턴)
    
    Args:
        interval_seconds: 데이터 수집 간격 (초 단위)
    
    Returns:
        DataScheduler 인스턴스
    """
    global _scheduler_instance
    
    if _scheduler_instance is None:
        _scheduler_instance = DataScheduler(interval_seconds=interval_seconds)
    
    return _scheduler_instance

