"""
Naver Finance 데이터 수집기

가격 데이터 및 매매 동향 데이터를 Naver Finance에서 수집합니다.
"""

from typing import List, Optional, Dict
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.database import get_db
from app.models import Stock, Price, TradingTrend
from app.utils.retry import retry_with_backoff
from app.utils.rate_limiter import RateLimiter
from app.utils.validators import validate_price_data, validate_trading_flow_data
import logging
import requests
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)

# 기본 Rate Limiter 설정 (0.5초 간격)
DEFAULT_RATE_LIMITER_INTERVAL = 0.5


class FinanceCollector:
    """Naver Finance 데이터 수집기"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        # Rate Limiter 초기화
        self.rate_limiter = RateLimiter(min_interval=DEFAULT_RATE_LIMITER_INTERVAL)
    
    @retry_with_backoff(
        max_retries=3,
        base_delay=1.0,
        exceptions=(requests.exceptions.RequestException, requests.exceptions.Timeout)
    )
    def fetch_naver_finance_prices(self, ticker: str, days: int = 10) -> List[dict]:
        """
        Naver Finance에서 가격 데이터 수집

        Args:
            ticker: 종목 코드 (예: "487240")
            days: 수집할 일수 (기본: 10일)

        Returns:
            수집된 가격 데이터 리스트
        """
        price_data = []
        page = 1
        max_pages = (days // 10) + 2  # 한 페이지당 10개씩, 여유있게 +2

        try:
            logger.info(f"Fetching up to {days} days of data from Naver Finance for {ticker}")

            while len(price_data) < days and page <= max_pages:
                url = f"https://finance.naver.com/item/sise_day.naver?code={ticker}&page={page}"
                logger.debug(f"Fetching page {page} for {ticker}")

                with self.rate_limiter:
                    response = requests.get(url, headers=self.headers, timeout=10)
                    response.raise_for_status()

                soup = BeautifulSoup(response.text, 'html.parser')

                # 시세 테이블 찾기
                table = soup.find('table', {'class': 'type2'})
                if not table:
                    logger.warning(f"Price table not found for {ticker} on page {page}")
                    break

                # 데이터 행 추출
                rows = table.find_all('tr')
                rows_parsed_this_page = 0

                for row in rows:
                    # 이미 충분한 데이터를 수집했으면 종료
                    if len(price_data) >= days:
                        break

                    cols = row.find_all('td')
                    if len(cols) >= 7:  # 날짜, 종가, 전일비, 시가, 고가, 저가, 거래량
                        date_cell = cols[0].get_text(strip=True)

                        # 날짜 형식 확인 (YYYY.MM.DD)
                        if date_cell and '.' in date_cell:
                            try:
                                # 데이터 파싱
                                date_str = date_cell  # 2025.11.07
                                close_price = self._parse_number(cols[1].get_text(strip=True))
                                change_str = cols[2].get_text(strip=True)  # 예: "상승205" 또는 "하락1,375"
                                open_price = self._parse_number(cols[3].get_text(strip=True))
                                high_price = self._parse_number(cols[4].get_text(strip=True))
                                low_price = self._parse_number(cols[5].get_text(strip=True))
                                volume = self._parse_number(cols[6].get_text(strip=True))

                                # 등락률 계산
                                change_rate = self._parse_change(change_str, close_price)
                                
                                # 등락액 계산
                                change_amount = None
                                if change_rate is not None and close_price is not None:
                                    # change_rate는 %이므로 이전 가격을 역산
                                    prev_price = close_price / (1 + change_rate / 100) if change_rate != 0 else close_price
                                    change_amount = close_price - prev_price

                                # 날짜 변환 (YYYY.MM.DD → YYYY-MM-DD)
                                date_obj = datetime.strptime(date_str, '%Y.%m.%d').date()

                                price_data.append({
                                    'ticker': ticker,
                                    'date': date_obj,
                                    'timestamp': datetime.now(),
                                    'current_price': close_price,
                                    'change_rate': change_rate,
                                    'change_amount': change_amount,
                                    'open_price': open_price,
                                    'high_price': high_price,
                                    'low_price': low_price,
                                    'volume': volume,
                                    'previous_close': None  # 전일 종가는 별도로 계산 필요
                                })
                                rows_parsed_this_page += 1

                            except Exception as e:
                                logger.warning(f"Failed to parse row for {ticker} on page {page}: {e}")
                                continue

                # 이번 페이지에서 아무 데이터도 파싱하지 못했으면 더 이상 페이지가 없는 것
                if rows_parsed_this_page == 0:
                    logger.info(f"No more data available for {ticker} after page {page}")
                    break

                page += 1

            logger.info(f"Collected {len(price_data)} price records for {ticker} from {page-1} pages")
            return price_data

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error while fetching {ticker}: {e}")
            return price_data  # 수집된 데이터라도 반환
        except Exception as e:
            logger.error(f"Unexpected error while fetching {ticker}: {e}")
            return price_data  # 수집된 데이터라도 반환
    
    def _parse_number(self, text: str) -> Optional[float]:
        """숫자 문자열을 float로 변환 (쉼표 제거)"""
        if not text or not text.strip():
            return None
        try:
            # 쉼표 제거 후 숫자로 변환
            cleaned = text.replace(',', '')
            return float(cleaned)
        except (ValueError, AttributeError):
            return None
    
    def _parse_change(self, change_str: str, close_price: Optional[float]) -> Optional[float]:
        """
        전일비 문자열을 등락률(%)로 변환
        
        Args:
            change_str: "상승205", "하락1,375", "보합0" 형식
            close_price: 현재 종가
        
        Returns:
            등락률 (%) 또는 None
        """
        if not change_str or not close_price or close_price == 0:
            return None
        
        try:
            # "상승", "하락", "보합" 제거하고 숫자만 추출
            number_str = re.sub(r'[^0-9,-]', '', change_str)
            if not number_str or number_str == '0':
                return 0.0
            
            change_amount = float(number_str.replace(',', ''))
            
            # 하락이면 음수로
            if '하락' in change_str:
                change_amount = -change_amount
            
            # 등락률 계산: (전일비 / (종가 - 전일비)) * 100
            prev_price = close_price - change_amount
            if prev_price != 0:
                return round((change_amount / prev_price) * 100, 2)
            
            return None
        except Exception as e:
            logger.warning(f"Failed to parse change string '{change_str}': {e}")
            return None
    
    def save_price_data(self, db: Session, price_data: List[dict]) -> int:
        """
        가격 데이터를 데이터베이스에 저장 (검증 및 정제 포함)
        
        벌크 insert를 사용하여 성능 최적화

        Args:
            db: 데이터베이스 세션
            price_data: 저장할 가격 데이터 리스트

        Returns:
            저장된 레코드 수
        """
        if not price_data:
            return 0

        # 모든 데이터를 먼저 검증하고 정제
        valid_data = []
        for data in price_data:
            # 데이터 검증
            is_valid, error_msg = validate_price_data(data)
            if not is_valid:
                logger.warning(f"Skipping invalid data for {data.get('ticker')} on {data.get('date')}: {error_msg}")
                continue

            # 데이터 정제
            cleaned_data = self.clean_price_data(data)
            valid_data.append(cleaned_data)

        if not valid_data:
            logger.warning("No valid price data to save after validation")
            return 0

        # 벌크 insert 수행
        saved_count = 0
        try:
            for data in valid_data:
                # 기존 데이터 확인 (ticker, date 기준)
                existing = db.query(Price).filter(
                    and_(
                        Price.ticker == data['ticker'],
                        Price.date == data['date']
                    )
                ).first()
                
                if existing:
                    # 업데이트
                    existing.timestamp = data['timestamp']
                    existing.current_price = data['current_price']
                    existing.change_rate = data['change_rate']
                    existing.change_amount = data['change_amount']
                    existing.open_price = data['open_price']
                    existing.high_price = data['high_price']
                    existing.low_price = data['low_price']
                    existing.volume = data['volume']
                    existing.previous_close = data.get('previous_close')
                else:
                    # 새로 추가
                    price = Price(**data)
                    db.add(price)
                
                saved_count += 1
            
            db.commit()
            logger.info(f"Saved {saved_count} price records to database (bulk insert)")

        except Exception as e:
            db.rollback()
            logger.error(f"Database error while saving price data: {e}")
            saved_count = 0  # 롤백 시 저장된 레코드 없음

        return saved_count
    
    def collect_and_save_prices(self, db: Session, ticker: str, days: int = 10) -> int:
        """
        Naver Finance에서 데이터 수집 후 데이터베이스에 저장
        
        Args:
            db: 데이터베이스 세션
            ticker: 종목 코드
            days: 수집할 일수
        
        Returns:
            저장된 레코드 수
        """
        logger.info(f"Starting price collection for {ticker} (last {days} days)")
        
        # 데이터 수집
        price_data = self.fetch_naver_finance_prices(ticker, days)
        
        if not price_data:
            logger.warning(f"No data collected for {ticker}")
            return 0
        
        # 데이터 저장
        saved_count = self.save_price_data(db, price_data)
        
        return saved_count
    
    @retry_with_backoff(
        max_retries=3,
        base_delay=1.0,
        exceptions=(requests.exceptions.RequestException, requests.exceptions.Timeout)
    )
    def fetch_naver_trading_flow(self, ticker: str, days: int = 10, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[dict]:
        """
        Naver Finance에서 투자자별 매매동향 데이터 수집 (다중 페이지 지원)

        Args:
            ticker: 종목 코드
            days: 수집할 일수 (기본: 10일)
            start_date: 시작 날짜 (선택, 지정 시 해당 날짜 이후 데이터만 수집)
            end_date: 종료 날짜 (선택, 지정 시 해당 날짜까지 데이터만 수집)

        Returns:
            수집된 매매동향 데이터 리스트
        """
        trading_data = []
        page = 1
        # 페이지당 약 10개 데이터, 여유있게 2페이지 추가
        max_pages = (days // 10) + 2
        
        # 날짜 범위가 지정된 경우, 실제 필요한 최대 데이터 수 계산
        target_count = days
        if start_date and end_date:
            target_count = days

        logger.info(f"Fetching trading flow from Naver Finance for {ticker} (target: {target_count} days, max pages: {max_pages}, date range: {start_date} to {end_date})")

        should_stop = False  # 전체 루프 종료 플래그

        while len(trading_data) < target_count and page <= max_pages and not should_stop:
            try:
                # Naver Finance 투자자별 매매동향 페이지 (페이지 파라미터 포함)
                url = f"https://finance.naver.com/item/frgn.naver?code={ticker}&page={page}"
                logger.info(f"Fetching trading flow page {page} for {ticker}")

                with self.rate_limiter:
                    response = requests.get(url, headers=self.headers, timeout=10)
                    response.raise_for_status()

                soup = BeautifulSoup(response.text, 'html.parser')

                # 매매동향 테이블 찾기 (두 번째 type2 테이블)
                # 첫 번째는 증권사별 매매, 두 번째가 투자자별 매매동향
                tables = soup.find_all('table', {'class': 'type2'})
                if len(tables) < 2:
                    logger.warning(f"Trading flow table not found for {ticker} on page {page}")
                    break

                table = tables[1]  # 두 번째 테이블 선택

                # 데이터 행 추출
                rows = table.find_all('tr')
                page_data_count = 0

                for row in rows:
                    # 이미 충분한 데이터를 수집했으면 중단
                    if len(trading_data) >= target_count:
                        break

                    cols = row.find_all('td')
                    # 실제 데이터 행은 7개 이상의 컬럼을 가짐
                    # [0]날짜 [1]종가 [2]전일비 [3]등락률 [4]거래량 [5]기관 [6]외국인 [7]외국인보유 [8]지분율
                    if len(cols) < 7:
                        continue

                    try:
                        # 날짜 추출
                        date_text = cols[0].get_text(strip=True)
                        if not date_text or date_text == '날짜' or '.' not in date_text:
                            continue

                        # 날짜 파싱 (YYYY.MM.DD 형식)
                        trade_date = datetime.strptime(date_text, '%Y.%m.%d').date()

                        # 날짜 범위 필터링 (지정된 경우)
                        if start_date and trade_date < start_date:
                            # 시작 날짜 이전 데이터를 만나면 더 이상 필요한 데이터가 없음
                            # (Naver Finance는 최신순으로 데이터 제공)
                            if len(trading_data) > 0:
                                # 이미 일부 데이터를 수집했으면 전체 루프 종료
                                should_stop = True
                                break
                            continue  # 시작 날짜 이전 데이터는 건너뜀
                        if end_date and trade_date > end_date:
                            continue  # 종료 날짜 이후 데이터는 건너뜀 (더 오래된 데이터가 나올 수 있으므로 계속 진행)

                        # 투자자별 순매수 추출 (천주 단위)
                        # 기관 (5번 컬럼)
                        institutional_text = cols[5].get_text(strip=True)
                        institutional_net = self._parse_trading_volume(institutional_text)

                        # 외국인 (6번 컬럼)
                        foreign_text = cols[6].get_text(strip=True)
                        foreign_net = self._parse_trading_volume(foreign_text)

                        # 개인 = -(기관 + 외국인)
                        # None 처리: 기관이나 외국인이 None이면 개인도 None
                        if institutional_net is not None and foreign_net is not None:
                            individual_net = -(institutional_net + foreign_net)
                        else:
                            individual_net = None

                        # 총 거래량 계산
                        total = None
                        if individual_net is not None and institutional_net is not None and foreign_net is not None:
                            total = abs(individual_net) + abs(institutional_net) + abs(foreign_net)

                        trading_data.append({
                            'ticker': ticker,
                            'date': trade_date,
                            'timestamp': datetime.now(),
                            'individual': individual_net,
                            'institution': institutional_net,
                            'foreign_investor': foreign_net,
                            'total': total
                        })

                        page_data_count += 1

                    except (ValueError, AttributeError, IndexError) as e:
                        logger.warning(f"Failed to parse trading flow row for {ticker} on page {page}: {e}")
                        continue

                logger.info(f"Collected {page_data_count} trading flow records from page {page} for {ticker} (total: {len(trading_data)})")

                # 현재 페이지에서 데이터가 없으면 더 이상 페이지가 없는 것으로 간주
                if page_data_count == 0:
                    logger.info(f"No more data found on page {page} for {ticker}, stopping pagination")
                    break

                page += 1

            except requests.exceptions.Timeout:
                logger.error(f"Timeout fetching trading flow page {page} for {ticker}")
                break
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error fetching trading flow page {page} for {ticker}: {e}")
                break
            except Exception as e:
                logger.error(f"Unexpected error fetching trading flow page {page} for {ticker}: {e}")
                break

        logger.info(f"Collected total {len(trading_data)} trading flow records for {ticker} from {page-1} pages")
        return trading_data
    
    def _parse_trading_volume(self, text: str) -> Optional[int]:
        """
        거래량 텍스트를 정수로 변환 (천주 단위)
        
        Args:
            text: 거래량 텍스트 (예: "1,234", "-5,678")
        
        Returns:
            정수로 변환된 거래량 (천주 단위), 실패 시 None
        """
        try:
            if not text or text.strip() == '':
                return None
            
            # 쉼표 제거 및 숫자 추출
            cleaned = text.replace(',', '').strip()
            
            # 빈 문자열이면 None
            if not cleaned or cleaned == '-':
                return None
            
            return int(cleaned)
            
        except (ValueError, AttributeError):
            return None
    
    def save_trading_flow_data(self, db: Session, trading_data: List[dict]) -> int:
        """
        매매동향 데이터를 데이터베이스에 저장

        Args:
            db: 데이터베이스 세션
            trading_data: 매매동향 데이터 리스트

        Returns:
            저장된 레코드 수
        """
        if not trading_data:
            logger.warning("No trading flow data to save")
            return 0

        # 데이터 검증
        valid_data = []
        for data in trading_data:
            if validate_trading_flow_data(data):
                valid_data.append(data)

        if not valid_data:
            logger.warning("No valid trading flow data after validation")
            return 0

        # 벌크 insert 수행
        saved_count = 0
        try:
            for data in valid_data:
                # 기존 데이터 확인 (ticker, date 기준)
                existing = db.query(TradingTrend).filter(
                    and_(
                        TradingTrend.ticker == data['ticker'],
                        TradingTrend.date == data['date']
                    )
                ).first()
                
                if existing:
                    # 업데이트
                    existing.timestamp = data['timestamp']
                    existing.individual = data['individual']
                    existing.institution = data['institution']
                    existing.foreign_investor = data['foreign_investor']
                    existing.total = data.get('total')
                else:
                    # 새로 추가
                    trading_trend = TradingTrend(**data)
                    db.add(trading_trend)
                
                saved_count += 1

            db.commit()
            logger.info(f"Saved {saved_count} trading flow records (bulk insert)")

        except Exception as e:
            logger.error(f"Database error saving trading flow: {e}")
            db.rollback()
            saved_count = 0  # 롤백 시 저장된 레코드 없음

        return saved_count

    def collect_and_save_trading_flow(self, db: Session, ticker: str, days: int = 10, start_date: Optional[date] = None, end_date: Optional[date] = None) -> int:
        """
        매매동향 데이터를 수집하고 저장
        
        Args:
            db: 데이터베이스 세션
            ticker: 종목 코드
            days: 수집할 일수
            start_date: 시작 날짜 (선택)
            end_date: 종료 날짜 (선택)
        
        Returns:
            저장된 레코드 수
        """
        logger.info(f"Starting trading flow collection for {ticker} (last {days} days, date range: {start_date} to {end_date})")
        
        # 데이터 수집
        trading_data = self.fetch_naver_trading_flow(ticker, days, start_date, end_date)
        
        if not trading_data:
            logger.warning(f"No trading flow data collected for {ticker}")
            return 0
        
        # 데이터 저장
        saved_count = self.save_trading_flow_data(db, trading_data)
        
        return saved_count
    
    
    def clean_price_data(self, data: dict) -> dict:
        """
        가격 데이터 정제 및 정규화
        
        Args:
            data: 정제할 가격 데이터
        
        Returns:
            정제된 가격 데이터
        """
        cleaned = data.copy()
        
        # 거래량이 None인 경우 0으로 처리
        if cleaned.get('volume') is None:
            cleaned['volume'] = 0
        
        # 거래량을 정수로 변환
        if isinstance(cleaned.get('volume'), float):
            cleaned['volume'] = int(cleaned['volume'])
        
        # 가격 필드를 소수점 2자리로 반올림 (누락된 필드는 None으로 유지)
        price_fields = ['open_price', 'high_price', 'low_price', 'current_price', 'change_amount', 'previous_close']
        for field in price_fields:
            if field not in cleaned:
                cleaned[field] = None
            elif cleaned[field] is not None:
                cleaned[field] = round(float(cleaned[field]), 2)
        
        # 등락률을 소수점 2자리로 반올림 (누락된 경우 None)
        if 'change_rate' not in cleaned:
            cleaned['change_rate'] = None
        elif cleaned['change_rate'] is not None:
            cleaned['change_rate'] = round(float(cleaned['change_rate']), 2)
        
        return cleaned
    

