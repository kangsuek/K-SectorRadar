"""pytest 설정 및 픽스처"""

import pytest
import os
from unittest.mock import Mock, patch

# 테스트 환경 변수 설정
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["REDIS_URL"] = "redis://localhost:6379/1"  # 테스트용 DB 1 사용


@pytest.fixture
def mock_redis_client():
    """Mock Redis 클라이언트 픽스처"""
    mock_client = Mock()
    mock_client.get.return_value = None
    mock_client.setex.return_value = True
    mock_client.delete.return_value = 1
    mock_client.ping.return_value = True
    mock_client.scan_iter.return_value = []
    return mock_client

