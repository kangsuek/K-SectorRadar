"""
데이터 검증 유틸리티

가격 데이터, 매매 동향 데이터, 뉴스 데이터의 유효성을 검증합니다.
"""

from typing import Optional
from datetime import date
import logging

logger = logging.getLogger(__name__)


def validate_price_data(data: dict) -> tuple[bool, Optional[str]]:
    """
    가격 데이터 유효성 검증
    
    Args:
        data: 검증할 가격 데이터
    
    Returns:
        (is_valid, error_message) 튜플
    """
    # 필수 필드 확인
    required_fields = ['ticker', 'date', 'current_price']
    for field in required_fields:
        if field not in data or data[field] is None:
            return False, f"Missing required field: {field}"
    
    # 날짜 타입 확인
    if not isinstance(data['date'], date):
        return False, f"Invalid date type: {type(data['date'])}"
    
    # 종가 검증 (양수)
    if data['current_price'] <= 0:
        return False, f"Invalid current_price: {data['current_price']} (must be > 0)"
    
    # 시가/고가/저가 검증 (있는 경우)
    for price_field in ['open_price', 'high_price', 'low_price']:
        if price_field in data and data[price_field] is not None:
            if data[price_field] <= 0:
                return False, f"Invalid {price_field}: {data[price_field]} (must be > 0)"
    
    # 거래량 검증 (0 이상)
    if 'volume' in data and data['volume'] is not None:
        if data['volume'] < 0:
            return False, f"Invalid volume: {data['volume']} (must be >= 0)"
    
    # 고가 >= 저가 검증
    if (data.get('high_price') is not None and 
        data.get('low_price') is not None):
        if data['high_price'] < data['low_price']:
            return False, f"high_price ({data['high_price']}) < low_price ({data['low_price']})"
    
    # 시가/고가/저가가 모두 있는 경우 범위 검증
    if (data.get('open_price') is not None and 
        data.get('high_price') is not None and 
        data.get('low_price') is not None):
        if not (data['low_price'] <= data['open_price'] <= data['high_price']):
            return False, f"open_price ({data['open_price']}) out of range [{data['low_price']}, {data['high_price']}]"
    
    # 종가 범위 검증
    if (data.get('high_price') is not None and 
        data.get('low_price') is not None):
        if not (data['low_price'] <= data['current_price'] <= data['high_price']):
            return False, f"current_price ({data['current_price']}) out of range [{data['low_price']}, {data['high_price']}]"
    
    return True, None


def validate_trading_flow_data(data: dict) -> bool:
    """
    매매동향 데이터 유효성 검증
    
    Args:
        data: 매매동향 데이터 딕셔너리
    
    Returns:
        유효하면 True, 아니면 False
    """
    # 필수 필드 확인
    required_fields = ['ticker', 'date']
    for field in required_fields:
        if field not in data or data[field] is None:
            logger.warning(f"Missing required field: {field}")
            return False
    
    # 날짜 타입 확인
    if not isinstance(data['date'], date):
        logger.warning(f"Invalid date type: {type(data['date'])}")
        return False
    
    # 적어도 하나의 매매동향 데이터가 있어야 함
    has_data = (
        data.get('individual') is not None or
        data.get('institution') is not None or
        data.get('foreign_investor') is not None
    )
    
    if not has_data:
        logger.warning("No trading flow data available")
        return False
    
    return True


def validate_news_data(data: dict) -> bool:
    """
    뉴스 데이터 유효성 검증
    
    Args:
        data: 뉴스 데이터 딕셔너리
    
    Returns:
        유효하면 True, 아니면 False
    """
    # 필수 필드 확인
    required_fields = ['ticker', 'title', 'url']
    for field in required_fields:
        if field not in data or data[field] is None:
            logger.warning(f"Missing required field: {field}")
            return False
    
    # URL 형식 검증 (간단한 검증)
    url = data.get('url', '')
    if not url.startswith('http://') and not url.startswith('https://'):
        logger.warning(f"Invalid URL format: {url}")
        return False
    
    return True

