"""pytest 설정 및 픽스처"""

import pytest
import os
import tempfile
from unittest.mock import Mock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# 테스트 환경 변수 설정
os.environ["ENVIRONMENT"] = "test"

# 임시 데이터베이스 파일 생성
_test_db_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
_test_db_path = _test_db_file.name
_test_db_file.close()

os.environ["DATABASE_URL"] = f"sqlite:///{_test_db_path}"
os.environ["REDIS_URL"] = "redis://localhost:6379/1"  # 테스트용 DB 1 사용

# 테스트용 데이터베이스 엔진 생성
_test_engine = create_engine(
    f"sqlite:///{_test_db_path}",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)

# Base는 나중에 import (순환 import 방지)


@pytest.fixture(scope="function")
def db_session():
    """데이터베이스 세션 픽스처"""
    # 순환 import 방지를 위해 여기서 import
    from app.db_base import Base
    
    # 테이블 생성
    Base.metadata.create_all(bind=_test_engine)
    
    # 세션 생성
    session = TestSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # 테이블 삭제
        Base.metadata.drop_all(bind=_test_engine)


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


@pytest.fixture(scope="function")
def client(mock_redis_client):
    """FastAPI 테스트 클라이언트 픽스처"""
    # 순환 import 방지를 위해 여기서 import
    from fastapi.testclient import TestClient
    from app.main import app
    from app.db_base import Base
    from app.database import get_db
    
    # startup/shutdown 이벤트 비활성화 (테스트 환경)
    app.router.on_startup.clear()
    app.router.on_shutdown.clear()
    
    # Redis 클라이언트 모킹
    with patch('app.utils.redis.get_redis_client', return_value=mock_redis_client):
        with patch('app.utils.cache.get_redis_client', return_value=mock_redis_client):
            with patch('app.main.test_redis_connection', return_value=True):
                # 데이터베이스 세션 오버라이드
                def override_get_db():
                    session = TestSessionLocal()
                    try:
                        yield session
                    finally:
                        session.close()
                
                # 기존 오버라이드 제거
                app.dependency_overrides.clear()
                app.dependency_overrides[get_db] = override_get_db
                
                # 테이블 생성
                Base.metadata.create_all(bind=_test_engine)
                
                with TestClient(app) as test_client:
                    yield test_client
                
                # 정리
                app.dependency_overrides.clear()
                Base.metadata.drop_all(bind=_test_engine)

