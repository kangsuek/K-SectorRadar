"""캐시 유틸리티 함수 및 데코레이터"""

import json
import hashlib
import functools
from typing import Any, Optional, Callable, Dict
from datetime import timedelta
import logging

from app.utils.redis import get_redis_client, test_redis_connection

logger = logging.getLogger(__name__)

# 기본 TTL (초)
DEFAULT_TTL = 3600  # 1시간


def _serialize_value(value: Any) -> str:
    """
    값을 JSON 문자열로 직렬화
    
    Args:
        value: 직렬화할 값
    
    Returns:
        str: JSON 문자열
    """
    return json.dumps(value, ensure_ascii=False, default=str)


def _deserialize_value(value: str) -> Any:
    """
    JSON 문자열을 값으로 역직렬화
    
    Args:
        value: 역직렬화할 JSON 문자열
    
    Returns:
        Any: 역직렬화된 값
    """
    return json.loads(value)


def _generate_cache_key(prefix: str, *args, **kwargs) -> str:
    """
    캐시 키 생성
    
    Args:
        prefix: 캐시 키 접두사
        *args: 위치 인자
        **kwargs: 키워드 인자
    
    Returns:
        str: 생성된 캐시 키
    """
    # 인자를 문자열로 변환하여 해시 생성
    key_parts = [prefix]
    
    if args:
        key_parts.append(str(args))
    
    if kwargs:
        # 키워드 인자를 정렬하여 일관된 키 생성
        sorted_kwargs = sorted(kwargs.items())
        key_parts.append(str(sorted_kwargs))
    
    key_string = ":".join(key_parts)
    # 해시를 사용하여 키 길이 제한
    key_hash = hashlib.md5(key_string.encode()).hexdigest()
    
    return f"{prefix}:{key_hash}"


def get_cache(key: str) -> Optional[Any]:
    """
    캐시에서 값 조회
    
    Args:
        key: 캐시 키
    
    Returns:
        Optional[Any]: 캐시된 값 (없으면 None)
    """
    try:
        client = get_redis_client()
        value = client.get(key)
        
        if value is None:
            return None
        
        return _deserialize_value(value)
    except Exception as e:
        logger.warning(f"캐시 조회 실패 (key: {key}): {e}")
        return None


def set_cache(key: str, value: Any, ttl: int = DEFAULT_TTL) -> bool:
    """
    캐시에 값 저장
    
    Args:
        key: 캐시 키
        value: 저장할 값
        ttl: TTL (초, 기본값: 1시간)
    
    Returns:
        bool: 저장 성공 여부
    """
    try:
        client = get_redis_client()
        serialized_value = _serialize_value(value)
        client.setex(key, ttl, serialized_value)
        return True
    except Exception as e:
        logger.warning(f"캐시 저장 실패 (key: {key}): {e}")
        return False


def delete_cache(key: str) -> bool:
    """
    캐시에서 값 삭제
    
    Args:
        key: 캐시 키
    
    Returns:
        bool: 삭제 성공 여부
    """
    try:
        client = get_redis_client()
        deleted = client.delete(key)
        return deleted > 0
    except Exception as e:
        logger.warning(f"캐시 삭제 실패 (key: {key}): {e}")
        return False


def clear_cache_pattern(pattern: str) -> int:
    """
    패턴에 맞는 캐시 키 삭제
    
    Args:
        pattern: 삭제할 캐시 키 패턴 (예: "stock:*", "price:*")
    
    Returns:
        int: 삭제된 키 개수
    """
    try:
        client = get_redis_client()
        deleted_count = 0
        
        # 패턴에 맞는 모든 키 조회
        for key in client.scan_iter(match=pattern):
            if client.delete(key):
                deleted_count += 1
        
        logger.info(f"캐시 패턴 삭제 완료 (pattern: {pattern}, count: {deleted_count})")
        return deleted_count
    except Exception as e:
        logger.warning(f"캐시 패턴 삭제 실패 (pattern: {pattern}): {e}")
        return 0


def cache_result(
    prefix: str,
    ttl: int = DEFAULT_TTL,
    key_func: Optional[Callable] = None
) -> Callable:
    """
    함수 결과를 캐시하는 데코레이터
    
    Args:
        prefix: 캐시 키 접두사
        ttl: TTL (초, 기본값: 1시간)
        key_func: 커스텀 캐시 키 생성 함수 (선택사항)
    
    Usage:
        @cache_result("stock", ttl=1800)
        def get_stock(ticker: str):
            # ...
            return stock_data
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 캐시 키 생성
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = _generate_cache_key(prefix, *args, **kwargs)
            
            # 캐시에서 조회 시도
            cached_value = get_cache(cache_key)
            if cached_value is not None:
                logger.debug(f"캐시 히트 (key: {cache_key})")
                return cached_value
            
            # 캐시 미스 - 함수 실행
            logger.debug(f"캐시 미스 (key: {cache_key})")
            result = func(*args, **kwargs)
            
            # 결과 캐시 저장
            set_cache(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


def invalidate_stock_cache(ticker: str) -> None:
    """
    종목 관련 캐시 무효화
    
    Args:
        ticker: 종목 코드
    """
    patterns = [
        f"stock:{ticker}",
        f"stock:*:{ticker}",
        f"price:{ticker}",
        f"price:*:{ticker}",
        f"trading:{ticker}",
        f"trading:*:{ticker}",
        f"news:{ticker}",
        f"news:*:{ticker}",
    ]
    
    total_deleted = 0
    for pattern in patterns:
        deleted = clear_cache_pattern(pattern)
        total_deleted += deleted
    
    logger.info(f"종목 캐시 무효화 완료 (ticker: {ticker}, deleted: {total_deleted})")


def invalidate_all_stocks_cache() -> None:
    """전체 종목 관련 캐시 무효화"""
    patterns = [
        "stock:*",
        "price:*",
        "trading:*",
        "news:*",
    ]
    
    total_deleted = 0
    for pattern in patterns:
        deleted = clear_cache_pattern(pattern)
        total_deleted += deleted
    
    logger.info(f"전체 종목 캐시 무효화 완료 (deleted: {total_deleted})")

