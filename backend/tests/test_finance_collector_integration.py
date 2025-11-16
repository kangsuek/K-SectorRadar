"""
Finance 수집기 실제 통합 테스트

실제 네트워크 요청을 사용하여 Naver Finance 데이터 수집기를 테스트합니다.
Mock을 사용하지 않고 실제 종목 데이터를 사용합니다.
"""

import pytest
from datetime import date, datetime
from decimal import Decimal

from app.collectors.finance_collector import FinanceCollector
from app.models.stock import Stock
from app.models.price import Price
from app.models.trading_trend import TradingTrend
from app.database import seed_stocks_from_json


class TestFinanceCollectorRealData:
    """실제 종목 데이터를 사용한 Finance 수집기 테스트"""
    
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
    
    def test_fetch_naver_finance_prices_real(self, setup_stocks, db_session):
        """실제 네트워크 요청으로 가격 데이터 수집 테스트"""
        collector = FinanceCollector()
        
        # 첫 번째 종목 선택 (ETF 또는 STOCK)
        stock = setup_stocks[0]
        ticker = stock.ticker
        
        print(f"\n[실제 테스트] {stock.name} ({ticker}) 가격 데이터 수집 중...")
        
        # 최근 5일 데이터 수집
        price_data = collector.fetch_naver_finance_prices(ticker, days=5)
        
        # 결과 검증
        assert len(price_data) > 0, f"{ticker}에 대한 가격 데이터를 수집하지 못했습니다."
        assert len(price_data) <= 5, "요청한 일수보다 많은 데이터가 수집되었습니다."
        
        # 첫 번째 데이터 검증
        first_data = price_data[0]
        assert first_data['ticker'] == ticker
        assert isinstance(first_data['date'], date)
        assert first_data['current_price'] is not None
        assert first_data['current_price'] > 0
        
        print(f"✅ {len(price_data)}개의 가격 데이터 수집 성공")
        print(f"   최신 날짜: {first_data['date']}, 종가: {first_data['current_price']}")
    
    def test_fetch_naver_trading_flow_real(self, setup_stocks, db_session):
        """실제 네트워크 요청으로 매매 동향 데이터 수집 테스트"""
        collector = FinanceCollector()
        
        # 첫 번째 종목 선택
        stock = setup_stocks[0]
        ticker = stock.ticker
        
        print(f"\n[실제 테스트] {stock.name} ({ticker}) 매매 동향 데이터 수집 중...")
        
        # 최근 5일 데이터 수집
        trading_data = collector.fetch_naver_trading_flow(ticker, days=5)
        
        # 결과 검증
        assert len(trading_data) > 0, f"{ticker}에 대한 매매 동향 데이터를 수집하지 못했습니다."
        assert len(trading_data) <= 5, "요청한 일수보다 많은 데이터가 수집되었습니다."
        
        # 첫 번째 데이터 검증
        first_data = trading_data[0]
        assert first_data['ticker'] == ticker
        assert isinstance(first_data['date'], date)
        
        # 적어도 하나의 투자자 데이터가 있어야 함
        has_data = (
            first_data.get('individual') is not None or
            first_data.get('institution') is not None or
            first_data.get('foreign_investor') is not None
        )
        assert has_data, "투자자별 매매 동향 데이터가 없습니다."
        
        print(f"✅ {len(trading_data)}개의 매매 동향 데이터 수집 성공")
        print(f"   최신 날짜: {first_data['date']}")
        print(f"   개인: {first_data.get('individual')}, 기관: {first_data.get('institution')}, 외국인: {first_data.get('foreign_investor')}")
    
    def test_collect_and_save_prices_real(self, setup_stocks, db_session):
        """실제 데이터 수집 및 저장 통합 테스트"""
        collector = FinanceCollector()
        
        # 첫 번째 종목 선택
        stock = setup_stocks[0]
        ticker = stock.ticker
        
        print(f"\n[실제 테스트] {stock.name} ({ticker}) 가격 데이터 수집 및 저장 중...")
        
        # 기존 데이터 확인
        existing_count = db_session.query(Price).filter(Price.ticker == ticker).count()
        print(f"   기존 가격 데이터: {existing_count}개")
        
        # 최근 3일 데이터 수집 및 저장
        saved_count = collector.collect_and_save_prices(db_session, ticker, days=3)
        
        # 결과 검증
        assert saved_count > 0, f"{ticker}에 대한 가격 데이터를 저장하지 못했습니다."
        assert saved_count <= 3, "요청한 일수보다 많은 데이터가 저장되었습니다."
        
        # 데이터베이스에서 확인
        saved_prices = db_session.query(Price).filter(Price.ticker == ticker).all()
        assert len(saved_prices) >= saved_count, "저장된 데이터 수가 일치하지 않습니다."
        
        # 최신 데이터 확인
        latest_price = db_session.query(Price).filter(
            Price.ticker == ticker
        ).order_by(Price.date.desc()).first()
        
        assert latest_price is not None
        assert latest_price.current_price > 0
        
        print(f"✅ {saved_count}개의 가격 데이터 저장 성공")
        print(f"   최신 날짜: {latest_price.date}, 종가: {latest_price.current_price}")
        print(f"   총 저장된 데이터: {len(saved_prices)}개")
    
    def test_collect_and_save_trading_flow_real(self, setup_stocks, db_session):
        """실제 매매 동향 데이터 수집 및 저장 통합 테스트"""
        collector = FinanceCollector()
        
        # 첫 번째 종목 선택
        stock = setup_stocks[0]
        ticker = stock.ticker
        
        print(f"\n[실제 테스트] {stock.name} ({ticker}) 매매 동향 데이터 수집 및 저장 중...")
        
        # 기존 데이터 확인
        existing_count = db_session.query(TradingTrend).filter(TradingTrend.ticker == ticker).count()
        print(f"   기존 매매 동향 데이터: {existing_count}개")
        
        # 최근 3일 데이터 수집 및 저장
        saved_count = collector.collect_and_save_trading_flow(db_session, ticker, days=3)
        
        # 결과 검증
        assert saved_count > 0, f"{ticker}에 대한 매매 동향 데이터를 저장하지 못했습니다."
        assert saved_count <= 3, "요청한 일수보다 많은 데이터가 저장되었습니다."
        
        # 데이터베이스에서 확인
        saved_trading = db_session.query(TradingTrend).filter(TradingTrend.ticker == ticker).all()
        assert len(saved_trading) >= saved_count, "저장된 데이터 수가 일치하지 않습니다."
        
        # 최신 데이터 확인
        latest_trading = db_session.query(TradingTrend).filter(
            TradingTrend.ticker == ticker
        ).order_by(TradingTrend.date.desc()).first()
        
        assert latest_trading is not None
        
        print(f"✅ {saved_count}개의 매매 동향 데이터 저장 성공")
        print(f"   최신 날짜: {latest_trading.date}")
        print(f"   개인: {latest_trading.individual}, 기관: {latest_trading.institution}, 외국인: {latest_trading.foreign_investor}")
        print(f"   총 저장된 데이터: {len(saved_trading)}개")
    
    def test_collect_all_stocks_real(self, setup_stocks, db_session):
        """모든 종목에 대한 실제 데이터 수집 테스트"""
        collector = FinanceCollector()
        
        stocks = setup_stocks
        print(f"\n[실제 테스트] {len(stocks)}개 종목 데이터 수집 중...")
        
        results = {}
        
        for stock in stocks[:3]:  # 처음 3개 종목만 테스트 (시간 절약)
            ticker = stock.ticker
            print(f"\n  {stock.name} ({ticker}) 처리 중...")
            
            try:
                # 가격 데이터 수집
                price_count = collector.collect_and_save_prices(db_session, ticker, days=2)
                
                # 매매 동향 데이터 수집
                trading_count = collector.collect_and_save_trading_flow(db_session, ticker, days=2)
                
                results[ticker] = {
                    'name': stock.name,
                    'price_count': price_count,
                    'trading_count': trading_count,
                    'success': price_count > 0
                }
                
                print(f"    ✅ 가격: {price_count}개, 매매동향: {trading_count}개")
                
            except Exception as e:
                results[ticker] = {
                    'name': stock.name,
                    'price_count': 0,
                    'trading_count': 0,
                    'success': False,
                    'error': str(e)
                }
                print(f"    ❌ 오류: {e}")
        
        # 결과 요약
        success_count = sum(1 for r in results.values() if r['success'])
        total_price = sum(r['price_count'] for r in results.values())
        total_trading = sum(r['trading_count'] for r in results.values())
        
        print(f"\n[결과 요약]")
        print(f"  성공: {success_count}/{len(results)}")
        print(f"  총 가격 데이터: {total_price}개")
        print(f"  총 매매 동향 데이터: {total_trading}개")
        
        # 최소한 하나는 성공해야 함
        assert success_count > 0, "모든 종목 데이터 수집에 실패했습니다."
    
    @pytest.mark.slow
    def test_collect_multiple_days_real(self, setup_stocks, db_session):
        """여러 일수 데이터 수집 테스트 (느린 테스트)"""
        collector = FinanceCollector()
        
        stock = setup_stocks[0]
        ticker = stock.ticker
        
        print(f"\n[실제 테스트] {stock.name} ({ticker}) - 여러 일수 데이터 수집 테스트")
        
        # 10일 데이터 수집
        saved_count = collector.collect_and_save_prices(db_session, ticker, days=10)
        
        assert saved_count > 0, "데이터 수집에 실패했습니다."
        assert saved_count <= 10, "요청한 일수보다 많은 데이터가 수집되었습니다."
        
        # 데이터베이스에서 날짜 범위 확인
        prices = db_session.query(Price).filter(
            Price.ticker == ticker
        ).order_by(Price.date.desc()).all()
        
        if len(prices) >= 2:
            latest_date = prices[0].date
            oldest_date = prices[-1].date
            date_range = (latest_date - oldest_date).days
            
            print(f"✅ {saved_count}개 데이터 수집, 날짜 범위: {date_range}일")
            assert date_range >= 0, "날짜 범위가 올바르지 않습니다."

