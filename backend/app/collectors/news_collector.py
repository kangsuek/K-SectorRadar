"""
Naver News 데이터 수집기

뉴스 데이터를 Naver Finance에서 수집합니다.
"""

from typing import List, Optional
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import and_
import hashlib
import uuid

from app.models import Stock, News
from app.utils.retry import retry_with_backoff
from app.utils.rate_limiter import RateLimiter
from app.utils.validators import validate_news_data
import logging
import requests
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)

# 기본 Rate Limiter 설정 (0.5초 간격)
DEFAULT_RATE_LIMITER_INTERVAL = 0.5


class NewsCollector:
    """Naver News 데이터 수집기"""
    
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
    def fetch_naver_news(self, ticker: str, max_items: int = 50) -> List[dict]:
        """
        Naver Finance에서 뉴스 데이터 수집

        Args:
            ticker: 종목 코드 (예: "487240")
            max_items: 최대 수집할 뉴스 개수 (기본: 50개)

        Returns:
            수집된 뉴스 데이터 리스트
        """
        news_data = []
        page = 1
        max_pages = (max_items // 20) + 2  # 한 페이지당 약 20개씩, 여유있게 +2

        try:
            logger.info(f"Fetching up to {max_items} news items from Naver Finance for {ticker}")

            while len(news_data) < max_items and page <= max_pages:
                url = f"https://finance.naver.com/item/news.naver?code={ticker}&page={page}"
                logger.debug(f"Fetching news page {page} for {ticker}")

                with self.rate_limiter:
                    response = requests.get(url, headers=self.headers, timeout=10)
                    response.raise_for_status()

                soup = BeautifulSoup(response.text, 'html.parser')

                # 뉴스 리스트 찾기
                news_list = soup.find('div', {'class': 'news_area'})
                if not news_list:
                    # 다른 형식의 뉴스 리스트 찾기
                    news_list = soup.find('table', {'class': 'type_1'})
                
                if not news_list:
                    logger.warning(f"News list not found for {ticker} on page {page}")
                    break

                # 뉴스 항목 추출
                news_items = news_list.find_all('tr') or news_list.find_all('li')
                items_parsed_this_page = 0

                for item in news_items:
                    # 이미 충분한 데이터를 수집했으면 종료
                    if len(news_data) >= max_items:
                        break

                    try:
                        # 제목과 링크 추출
                        title_link = item.find('a')
                        if not title_link:
                            continue

                        title = title_link.get_text(strip=True)
                        url = title_link.get('href', '')
                        
                        # 상대 URL을 절대 URL로 변환
                        if url and not url.startswith('http'):
                            if url.startswith('/'):
                                url = f"https://finance.naver.com{url}"
                            else:
                                url = f"https://finance.naver.com/item/{url}"

                        if not title or not url:
                            continue

                        # 출처 추출
                        source = None
                        source_elem = item.find('span', {'class': 'press'}) or item.find('span', {'class': 'info'})
                        if source_elem:
                            source = source_elem.get_text(strip=True)

                        # 발행 날짜 추출
                        published_at = None
                        date_elem = item.find('span', {'class': 'date'}) or item.find('td', {'class': 'date'})
                        if date_elem:
                            date_text = date_elem.get_text(strip=True)
                            published_at = self._parse_date(date_text)

                        # 고유 ID 생성 (URL 기반 해시)
                        news_id = self._generate_news_id(url, ticker)
                        # URL 해시 생성 (UNIQUE 제약조건용)
                        url_hash = self._generate_url_hash(url)

                        news_data.append({
                            'id': news_id,
                            'ticker': ticker,
                            'title': title,
                            'url': url,
                            'url_hash': url_hash,
                            'source': source,
                            'published_at': published_at,
                            'timestamp': datetime.now(),
                        })
                        items_parsed_this_page += 1

                    except Exception as e:
                        logger.warning(f"Failed to parse news item for {ticker} on page {page}: {e}")
                        continue

                # 이번 페이지에서 아무 데이터도 파싱하지 못했으면 더 이상 페이지가 없는 것
                if items_parsed_this_page == 0:
                    logger.info(f"No more news available for {ticker} after page {page}")
                    break

                page += 1

            logger.info(f"Collected {len(news_data)} news items for {ticker} from {page-1} pages")
            return news_data

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error while fetching news for {ticker}: {e}")
            return news_data  # 수집된 데이터라도 반환
        except Exception as e:
            logger.error(f"Unexpected error while fetching news for {ticker}: {e}")
            return news_data  # 수집된 데이터라도 반환
    
    def _parse_date(self, date_text: str) -> Optional[datetime]:
        """
        날짜 문자열을 datetime으로 변환
        
        Args:
            date_text: 날짜 문자열 (예: "2025.11.14", "11.14", "1시간 전")
        
        Returns:
            datetime 객체 또는 None
        """
        if not date_text:
            return None
        
        try:
            # "YYYY.MM.DD" 형식
            if re.match(r'\d{4}\.\d{2}\.\d{2}', date_text):
                return datetime.strptime(date_text, '%Y.%m.%d')
            
            # "MM.DD" 형식 (올해로 가정)
            if re.match(r'\d{2}\.\d{2}', date_text):
                current_year = datetime.now().year
                return datetime.strptime(f"{current_year}.{date_text}", '%Y.%m.%d')
            
            # "N시간 전", "N분 전" 등의 상대 시간은 현재 시간으로 처리
            if '시간' in date_text or '분' in date_text or '일' in date_text:
                return datetime.now()
            
            return None
        except Exception as e:
            logger.warning(f"Failed to parse date '{date_text}': {e}")
            return None
    
    def _generate_news_id(self, url: str, ticker: str) -> str:
        """
        뉴스 고유 ID 생성 (URL 기반 해시)
        
        Args:
            url: 뉴스 URL
            ticker: 종목 코드
        
        Returns:
            고유 ID 문자열
        """
        # URL과 ticker를 조합하여 해시 생성
        combined = f"{ticker}:{url}"
        hash_obj = hashlib.md5(combined.encode('utf-8'))
        return hash_obj.hexdigest()[:50]  # 최대 50자
    
    def _generate_url_hash(self, url: str) -> str:
        """
        URL 해시 생성 (UNIQUE 제약조건용)
        
        Args:
            url: 뉴스 URL
        
        Returns:
            SHA256 해시 문자열 (64자)
        """
        hash_obj = hashlib.sha256(url.encode('utf-8'))
        return hash_obj.hexdigest()
    
    def save_news_data(self, db: Session, news_data: List[dict]) -> int:
        """
        뉴스 데이터를 데이터베이스에 저장 (검증 및 정제 포함)

        Args:
            db: 데이터베이스 세션
            news_data: 저장할 뉴스 데이터 리스트

        Returns:
            저장된 레코드 수
        """
        if not news_data:
            return 0

        # 모든 데이터를 먼저 검증하고 정제
        valid_data = []
        for data in news_data:
            # 데이터 검증
            if not validate_news_data(data):
                title_preview = data.get('title', '')[:50] if data.get('title') else 'N/A'
                logger.warning(f"Skipping invalid news data for {data.get('ticker')}: {title_preview}")
                continue

            # 데이터 정제
            cleaned_data = self.clean_news_data(data)
            valid_data.append(cleaned_data)

        if not valid_data:
            logger.warning("No valid news data to save after validation")
            return 0

        # 벌크 insert 수행
        saved_count = 0
        try:
            for data in valid_data:
                # 기존 데이터 확인 (url_hash 기준 - 가장 빠름)
                existing = db.query(News).filter(
                    News.url_hash == data.get('url_hash')
                ).first()
                
                if not existing:
                    # id로도 확인 (하위 호환성)
                    existing = db.query(News).filter(
                        News.id == data['id']
                    ).first()
                
                if not existing:
                    # URL로도 확인 (id가 다른 경우 대비)
                    existing = db.query(News).filter(
                        News.url == data['url']
                    ).first()
                
                if existing:
                    # 업데이트
                    existing.title = data['title']
                    existing.source = data.get('source')
                    existing.published_at = data.get('published_at')
                    existing.collected_at = data.get('collected_at', data.get('timestamp', datetime.now()))
                    # url_hash가 없으면 추가
                    if not existing.url_hash and data.get('url_hash'):
                        existing.url_hash = data['url_hash']
                else:
                    # 새로 추가 (url_hash가 없으면 생성)
                    if 'url_hash' not in data or not data.get('url_hash'):
                        data['url_hash'] = self._generate_url_hash(data['url'])
                    news = News(**data)
                    db.add(news)
                
                saved_count += 1
            
            db.commit()
            logger.info(f"Saved {saved_count} news records to database (bulk insert)")

        except Exception as e:
            db.rollback()
            logger.error(f"Database error while saving news data: {e}")
            saved_count = 0  # 롤백 시 저장된 레코드 없음

        return saved_count
    
    def collect_and_save_news(self, db: Session, ticker: str, max_items: int = 50) -> int:
        """
        Naver Finance에서 뉴스 데이터 수집 후 데이터베이스에 저장
        
        Args:
            db: 데이터베이스 세션
            ticker: 종목 코드
            max_items: 최대 수집할 뉴스 개수
        
        Returns:
            저장된 레코드 수
        """
        logger.info(f"Starting news collection for {ticker} (max {max_items} items)")
        
        # 데이터 수집
        news_data = self.fetch_naver_news(ticker, max_items)
        
        if not news_data:
            logger.warning(f"No news data collected for {ticker}")
            return 0
        
        # 데이터 저장
        saved_count = self.save_news_data(db, news_data)
        
        return saved_count
    
    def clean_news_data(self, data: dict) -> dict:
        """
        뉴스 데이터 정제 및 정규화
        
        Args:
            data: 정제할 뉴스 데이터
        
        Returns:
            정제된 뉴스 데이터
        """
        cleaned = data.copy()
        
        # 제목 길이 제한 (500자)
        if 'title' in cleaned and cleaned['title']:
            cleaned['title'] = cleaned['title'][:500]
        
        # URL 길이 제한 (1000자)
        if 'url' in cleaned and cleaned['url']:
            cleaned['url'] = cleaned['url'][:1000]
        
        # 출처 길이 제한 (100자)
        if 'source' in cleaned and cleaned['source']:
            cleaned['source'] = cleaned['source'][:100]
        
        # timestamp를 collected_at으로 변경
        if 'timestamp' in cleaned:
            cleaned['collected_at'] = cleaned['timestamp']
            del cleaned['timestamp']
        
        return cleaned

