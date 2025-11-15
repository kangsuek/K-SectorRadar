"""Health Check API 테스트"""

import pytest
from unittest.mock import patch, Mock


class TestHealthCheck:
    """Health Check 엔드포인트 테스트"""
    
    def test_health_check_success(self, client):
        """Health Check 성공 테스트"""
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "database" in data
        assert "redis" in data
        assert "timestamp" in data
        assert data["status"] in ["healthy", "unhealthy"]
        assert data["database"] in ["connected", "disconnected"]
        assert data["redis"] in ["connected", "disconnected"]
    
    def test_health_check_database_connected(self, client):
        """데이터베이스 연결 상태 확인 테스트"""
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # 테스트 환경에서는 데이터베이스가 연결되어 있어야 함
        assert data["database"] == "connected"
    
    def test_health_check_redis_status(self, client):
        """Redis 연결 상태 확인 테스트"""
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Redis 상태는 모킹되어 있으므로 connected 또는 disconnected일 수 있음
        assert data["redis"] in ["connected", "disconnected"]
    
    def test_health_check_structure(self, client):
        """Health Check 응답 구조 테스트"""
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # 필수 필드 확인
        required_fields = ["status", "database", "redis", "timestamp"]
        for field in required_fields:
            assert field in data, f"필수 필드 '{field}'가 없습니다"
        
        # timestamp 형식 확인 (ISO 형식)
        assert "T" in data["timestamp"] or "-" in data["timestamp"]
    
    @patch('app.main.test_redis_connection')
    def test_health_check_redis_disconnected(self, mock_redis_test, client):
        """Redis 연결 실패 시 Health Check 테스트"""
        mock_redis_test.return_value = False
        
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["redis"] == "disconnected"
        # 데이터베이스는 연결되어 있으면 healthy
        if data["database"] == "connected":
            assert data["status"] == "healthy"
    
    @patch('app.main.engine')
    def test_health_check_database_disconnected(self, mock_engine, client):
        """데이터베이스 연결 실패 시 Health Check 테스트"""
        # 데이터베이스 연결 실패 시뮬레이션
        mock_engine.connect.side_effect = Exception("Database connection failed")
        
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["database"] == "disconnected"
        assert data["status"] == "unhealthy"


class TestRootEndpoint:
    """루트 엔드포인트 테스트"""
    
    def test_root_endpoint(self, client):
        """루트 엔드포인트 테스트"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "version" in data
        assert data["message"] == "K-SectorRadar API"
        assert data["version"] == "1.0.0"

