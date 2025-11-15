"""Redis 클라이언트 유틸리티"""

import redis
from typing import Optional
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Redis 클라이언트 인스턴스 (싱글톤 패턴)
_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> redis.Redis:
    """
    Redis 클라이언트 인스턴스 반환 (싱글톤 패턴)
    
    Returns:
        redis.Redis: Redis 클라이언트 인스턴스
    
    Raises:
        redis.ConnectionError: Redis 연결 실패 시
    """
    global _redis_client
    
    if _redis_client is None:
        try:
            _redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,  # 문자열 자동 디코딩
                socket_connect_timeout=5,  # 연결 타임아웃 5초
                socket_timeout=5,  # 소켓 타임아웃 5초
                retry_on_timeout=True,  # 타임아웃 시 재시도
                health_check_interval=30,  # 30초마다 헬스 체크
            )
            # 연결 테스트
            _redis_client.ping()
            logger.info("Redis 연결 성공")
        except redis.ConnectionError as e:
            logger.error(f"Redis 연결 실패: {e}")
            raise
        except Exception as e:
            logger.error(f"Redis 초기화 오류: {e}")
            raise
    
    return _redis_client


def close_redis_client() -> None:
    """Redis 클라이언트 연결 종료"""
    global _redis_client
    
    if _redis_client is not None:
        try:
            _redis_client.close()
            logger.info("Redis 연결 종료")
        except Exception as e:
            logger.error(f"Redis 연결 종료 오류: {e}")
        finally:
            _redis_client = None


def test_redis_connection() -> bool:
    """
    Redis 연결 테스트
    
    Returns:
        bool: 연결 성공 여부
    """
    try:
        client = get_redis_client()
        client.ping()
        return True
    except Exception as e:
        logger.error(f"Redis 연결 테스트 실패: {e}")
        return False

