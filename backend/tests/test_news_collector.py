"""
News 수집기 단위 테스트
"""

import pytest
from unittest.mock import patch, Mock, MagicMock
from datetime import datetime, date
from bs4 import BeautifulSoup

from app.collectors.news_collector import NewsCollector
from app.models.stock import Stock
from app.models.news import News


class TestNewsCollectorInit:
    """NewsCollector 초기화 테스트"""
    
    def test_init(self):
        """수집기 초기화 테스트"""
        collector = NewsCollector()
        
        assert collector is not None
        assert 'User-Agent' in collector.headers
        assert collector.rate_limiter is not None


class TestNewsCollectorParsing:
    """NewsCollector 파싱 메서드 테스트"""
    
    @pytest.fixture
    def collector(self):
        """수집기 픽스처"""
        return NewsCollector()
    
    def test_parse_date_full_format(self, collector):
        """전체 날짜 형식 파싱 테스트 (YYYY.MM.DD)"""
        result = collector._parse_date("2025.11.14")
        assert result is not None
        assert result.year == 2025
        assert result.month == 11
        assert result.day == 14
    
    def test_parse_date_partial_format(self, collector):
        """부분 날짜 형식 파싱 테스트 (MM.DD)"""
        result = collector._parse_date("11.14")
        assert result is not None
        assert result.month == 11
        assert result.day == 14
        # 올해로 가정
        assert result.year == datetime.now().year
    
    def test_parse_date_relative_time(self, collector):
        """상대 시간 파싱 테스트"""
        result = collector._parse_date("1시간 전")
        assert result is not None
        # 현재 시간으로 처리되므로 None이 아님
        
        result = collector._parse_date("30분 전")
        assert result is not None
        
        result = collector._parse_date("2일 전")
        assert result is not None
    
    def test_parse_date_invalid(self, collector):
        """유효하지 않은 날짜 파싱 테스트"""
        assert collector._parse_date("") is None
        assert collector._parse_date("invalid") is None
        assert collector._parse_date(None) is None
    
    def test_generate_news_id(self, collector):
        """뉴스 ID 생성 테스트"""
        url = "https://finance.naver.com/item/news_read.naver?article_id=123456"
        ticker = "487240"
        
        news_id = collector._generate_news_id(url, ticker)
        
        assert news_id is not None
        assert len(news_id) <= 50
        assert isinstance(news_id, str)
        
        # 같은 입력에 대해 같은 ID 생성
        news_id2 = collector._generate_news_id(url, ticker)
        assert news_id == news_id2
        
        # 다른 URL에 대해 다른 ID 생성
        url2 = "https://finance.naver.com/item/news_read.naver?article_id=789012"
        news_id3 = collector._generate_news_id(url2, ticker)
        assert news_id != news_id3


class TestNewsCollectorDataCleaning:
    """NewsCollector 데이터 정제 메서드 테스트"""
    
    @pytest.fixture
    def collector(self):
        """수집기 픽스처"""
        return NewsCollector()
    
    def test_clean_news_data(self, collector):
        """뉴스 데이터 정제 테스트"""
        data = {
            'id': 'test_id',
            'ticker': '487240',
            'title': 'A' * 600,  # 500자 초과
            'url': 'B' * 1200,  # 1000자 초과
            'source': 'C' * 150,  # 100자 초과
            'timestamp': datetime.now()
        }
        
        cleaned = collector.clean_news_data(data)
        
        assert len(cleaned['title']) == 500
        assert len(cleaned['url']) == 1000
        assert len(cleaned['source']) == 100
        assert 'collected_at' in cleaned
        assert 'timestamp' not in cleaned
    
    def test_clean_news_data_normal_length(self, collector):
        """정상 길이 데이터 정제 테스트"""
        data = {
            'id': 'test_id',
            'ticker': '487240',
            'title': 'Normal Title',
            'url': 'https://example.com/news',
            'source': 'Test Source',
            'timestamp': datetime.now()
        }
        
        cleaned = collector.clean_news_data(data)
        
        assert cleaned['title'] == 'Normal Title'
        assert cleaned['url'] == 'https://example.com/news'
        assert cleaned['source'] == 'Test Source'
        assert 'collected_at' in cleaned


class TestNewsCollectorFetch:
    """NewsCollector 데이터 수집 메서드 테스트"""
    
    @pytest.fixture
    def collector(self):
        """수집기 픽스처"""
        return NewsCollector()
    
    @patch('app.collectors.news_collector.requests.get')
    def test_fetch_naver_news_success(self, mock_get, collector):
        """뉴스 데이터 수집 성공 테스트"""
        # Mock HTML 응답
        html_content = """
        <html>
        <body>
            <div class="news_area">
                <tr>
                    <td><a href="/item/news_read.naver?article_id=123">뉴스 제목 1</a></td>
                    <td><span class="press">조선일보</span></td>
                    <td><span class="date">2025.11.14</span></td>
                </tr>
                <tr>
                    <td><a href="/item/news_read.naver?article_id=456">뉴스 제목 2</a></td>
                    <td><span class="press">한국경제</span></td>
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
        
        data = collector.fetch_naver_news("487240", max_items=2)
        
        assert len(data) == 2
        assert data[0]['ticker'] == "487240"
        assert "뉴스 제목" in data[0]['title']
        assert data[0]['url'].startswith("https://finance.naver.com")
        assert data[0]['id'] is not None
    
    @patch('app.collectors.news_collector.requests.get')
    def test_fetch_naver_news_table_format(self, mock_get, collector):
        """테이블 형식 뉴스 리스트 테스트"""
        html_content = """
        <html>
        <body>
            <table class="type_1">
                <tr>
                    <td><a href="/item/news_read.naver?article_id=789">테이블 형식 뉴스</a></td>
                    <td class="date">2025.11.12</td>
                </tr>
            </table>
        </body>
        </html>
        """
        
        mock_response = Mock()
        mock_response.text = html_content
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        data = collector.fetch_naver_news("487240", max_items=1)
        
        assert len(data) >= 1
        assert data[0]['ticker'] == "487240"
    
    @patch('app.collectors.news_collector.requests.get')
    def test_fetch_naver_news_no_list_found(self, mock_get, collector):
        """뉴스 리스트를 찾을 수 없는 경우 테스트"""
        mock_response = Mock()
        mock_response.text = "<html><body>No news here</body></html>"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        data = collector.fetch_naver_news("487240", max_items=10)
        
        assert len(data) == 0
    
    @patch('app.collectors.news_collector.requests.get')
    def test_fetch_naver_news_network_error(self, mock_get, collector):
        """네트워크 오류 테스트"""
        import requests
        mock_get.side_effect = requests.exceptions.RequestException("Network error")
        
        data = collector.fetch_naver_news("487240", max_items=10)
        
        # 재시도 후에도 실패하면 빈 리스트 반환
        assert len(data) == 0
    
    @patch('app.collectors.news_collector.requests.get')
    def test_fetch_naver_news_max_items_limit(self, mock_get, collector):
        """최대 개수 제한 테스트"""
        # 여러 페이지의 뉴스 데이터 생성
        html_content = """
        <html>
        <body>
            <div class="news_area">
                <tr><td><a href="/item/news_read.naver?article_id={}">뉴스 {}</a></td></tr>
            </div>
        </body>
        </html>
        """
        
        def side_effect(*args, **kwargs):
            page = kwargs.get('params', {}).get('page', 1) if 'params' in kwargs else 1
            # URL에서 page 추출 (간단한 예시)
            url = args[0] if args else ""
            if 'page=2' in url:
                page = 2
            
            content = ""
            for i in range(1, 21):  # 페이지당 20개
                content += f'<tr><td><a href="/item/news_read.naver?article_id={page*100+i}">뉴스 {page*100+i}</a></td></tr>'
            
            mock_resp = Mock()
            mock_resp.text = f"<html><body><div class='news_area'>{content}</div></body></html>"
            mock_resp.raise_for_status = Mock()
            return mock_resp
        
        mock_get.side_effect = side_effect
        
        data = collector.fetch_naver_news("487240", max_items=15)
        
        # 최대 15개까지만 수집
        assert len(data) <= 15


class TestNewsCollectorSave:
    """NewsCollector 데이터 저장 메서드 테스트"""
    
    @pytest.fixture
    def collector(self):
        """수집기 픽스처"""
        return NewsCollector()
    
    def test_save_news_data_empty(self, collector, db_session):
        """빈 뉴스 데이터 저장 테스트"""
        saved_count = collector.save_news_data(db_session, [])
        assert saved_count == 0
    
    def test_save_news_data_valid(self, collector, db_session):
        """유효한 뉴스 데이터 저장 테스트"""
        # 종목 생성
        stock = Stock(ticker="NEWS001", name="뉴스 테스트", type="STOCK")
        db_session.add(stock)
        db_session.commit()
        
        # 뉴스 데이터
        url = 'https://finance.naver.com/item/news_read.naver?article_id=123'
        news_data = [{
            'id': 'test_news_id_1',
            'ticker': "NEWS001",
            'title': '테스트 뉴스 제목',
            'url': url,
            'url_hash': collector._generate_url_hash(url),
            'source': '테스트 출처',
            'published_at': datetime(2025, 11, 14, 10, 0, 0),
            'timestamp': datetime.now()
        }]
        
        saved_count = collector.save_news_data(db_session, news_data)
        assert saved_count == 1
        
        # 데이터베이스에서 확인
        saved_news = db_session.query(News).filter(News.id == 'test_news_id_1').first()
        assert saved_news is not None
        assert saved_news.title == '테스트 뉴스 제목'
        assert saved_news.ticker == "NEWS001"
    
    def test_save_news_data_invalid(self, collector, db_session):
        """유효하지 않은 뉴스 데이터 저장 테스트"""
        # 종목 생성
        stock = Stock(ticker="INVALID001", name="무효 뉴스", type="STOCK")
        db_session.add(stock)
        db_session.commit()
        
        # 유효하지 않은 데이터 (필수 필드 누락)
        news_data = [{
            'id': 'invalid_news_id',
            'ticker': "INVALID001",
            # 'title' 필드 누락
            'url': 'https://example.com/news',
            'timestamp': datetime.now()
        }]
        
        saved_count = collector.save_news_data(db_session, news_data)
        assert saved_count == 0  # 검증 실패로 저장되지 않음
    
    def test_save_news_data_update_existing(self, collector, db_session):
        """기존 뉴스 데이터 업데이트 테스트"""
        # 종목 생성
        stock = Stock(ticker="UPDATE001", name="업데이트 뉴스", type="STOCK")
        db_session.add(stock)
        db_session.commit()
        
        # 기존 뉴스 데이터
        url = 'https://finance.naver.com/item/news_read.naver?article_id=123'
        existing_news = News(
            id='existing_news_id',
            ticker="UPDATE001",
            title='기존 제목',
            url=url,
            url_hash=collector._generate_url_hash(url),
            source='기존 출처',
            published_at=datetime(2025, 11, 13, 10, 0, 0),
            collected_at=datetime(2025, 11, 13, 10, 0, 0)
        )
        db_session.add(existing_news)
        db_session.commit()
        
        # 업데이트할 데이터
        url = 'https://finance.naver.com/item/news_read.naver?article_id=123'
        news_data = [{
            'id': 'existing_news_id',
            'ticker': "UPDATE001",
            'title': '업데이트된 제목',
            'url': url,
            'url_hash': collector._generate_url_hash(url),
            'source': '업데이트된 출처',
            'published_at': datetime(2025, 11, 14, 10, 0, 0),
            'timestamp': datetime.now()
        }]
        
        saved_count = collector.save_news_data(db_session, news_data)
        assert saved_count == 1
        
        # 업데이트 확인
        updated_news = db_session.query(News).filter(News.id == 'existing_news_id').first()
        assert updated_news.title == '업데이트된 제목'
        assert updated_news.source == '업데이트된 출처'
    
    def test_save_news_data_duplicate_url(self, collector, db_session):
        """중복 URL 처리 테스트"""
        # 종목 생성
        stock = Stock(ticker="DUPLICATE001", name="중복 뉴스", type="STOCK")
        db_session.add(stock)
        db_session.commit()
        
        url = 'https://finance.naver.com/item/news_read.naver?article_id=456'
        
        # 첫 번째 뉴스 데이터
        news_data1 = [{
            'id': 'news_id_1',
            'ticker': "DUPLICATE001",
            'title': '첫 번째 뉴스',
            'url': url,
            'url_hash': collector._generate_url_hash(url),
            'source': '출처 1',
            'published_at': datetime(2025, 11, 14, 10, 0, 0),
            'timestamp': datetime.now()
        }]
        
        saved_count1 = collector.save_news_data(db_session, news_data1)
        assert saved_count1 == 1
        
        # 같은 URL의 다른 ID로 저장 시도
        news_data2 = [{
            'id': 'news_id_2',  # 다른 ID
            'ticker': "DUPLICATE001",
            'title': '두 번째 뉴스',
            'url': url,  # 같은 URL
            'url_hash': collector._generate_url_hash(url),  # 같은 URL이므로 같은 해시
            'source': '출처 2',
            'published_at': datetime(2025, 11, 14, 11, 0, 0),
            'timestamp': datetime.now()
        }]
        
        saved_count2 = collector.save_news_data(db_session, news_data2)
        assert saved_count2 == 1  # 업데이트로 처리
        
        # 같은 URL이므로 하나만 존재해야 함
        news_count = db_session.query(News).filter(News.url == url).count()
        assert news_count == 1


class TestNewsCollectorIntegration:
    """NewsCollector 통합 테스트"""
    
    @pytest.fixture
    def collector(self):
        """수집기 픽스처"""
        return NewsCollector()
    
    @patch('app.collectors.news_collector.requests.get')
    def test_collect_and_save_news_integration(self, mock_get, collector, db_session):
        """뉴스 데이터 수집 및 저장 통합 테스트"""
        # 종목 생성
        stock = Stock(ticker="INTEG001", name="통합 뉴스 테스트", type="STOCK")
        db_session.add(stock)
        db_session.commit()
        
        # Mock HTML 응답
        html_content = """
        <html>
        <body>
            <div class="news_area">
                <tr>
                    <td><a href="/item/news_read.naver?article_id=123">통합 테스트 뉴스</a></td>
                    <td><span class="press">테스트 출처</span></td>
                    <td><span class="date">2025.11.14</span></td>
                </tr>
            </div>
        </body>
        </html>
        """
        
        mock_response = Mock()
        mock_response.text = html_content
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # 수집 및 저장
        saved_count = collector.collect_and_save_news(db_session, "INTEG001", max_items=1)
        
        assert saved_count == 1
        
        # 데이터베이스에서 확인
        saved_news = db_session.query(News).filter(News.ticker == "INTEG001").first()
        assert saved_news is not None
        assert "통합 테스트" in saved_news.title
        assert saved_news.url.startswith("https://finance.naver.com")

