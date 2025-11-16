"""
스케줄러 API 테스트
"""

import pytest
from unittest.mock import patch, Mock, MagicMock
from datetime import datetime

from app.models.stock import Stock
from app.scheduler.data_scheduler import DataScheduler, get_scheduler


class TestSchedulerStatusAPI:
    """스케줄러 상태 조회 API 테스트"""
    
    def test_get_scheduler_status(self, client):
        """스케줄러 상태 조회 테스트"""
        response = client.get("/api/scheduler/status")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "data" in data
        assert "is_running" in data["data"]
        assert "interval_seconds" in data["data"]
        assert "next_run_time" in data["data"] or data["data"]["next_run_time"] is None
        assert "last_run_time" in data["data"] or data["data"]["last_run_time"] is None
        assert "last_run_status" in data["data"] or data["data"]["last_run_status"] is None


class TestSchedulerStartAPI:
    """스케줄러 시작 API 테스트"""
    
    def test_start_scheduler_default_interval(self, client):
        """기본 간격으로 스케줄러 시작 테스트"""
        # 먼저 중지 (이미 실행 중일 수 있음)
        client.post("/api/scheduler/stop")
        
        response = client.post("/api/scheduler/start")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["data"]["is_running"] is True
        assert data["data"]["interval_seconds"] == 30  # 기본값
        assert "Scheduler started successfully" in data["message"]
        
        # 정리
        client.post("/api/scheduler/stop")
    
    def test_start_scheduler_custom_interval(self, client):
        """사용자 지정 간격으로 스케줄러 시작 테스트"""
        # 먼저 중지
        client.post("/api/scheduler/stop")
        
        response = client.post("/api/scheduler/start?interval_seconds=60")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["data"]["is_running"] is True
        assert data["data"]["interval_seconds"] == 60
        assert "Scheduler started successfully" in data["message"]
        
        # 정리
        client.post("/api/scheduler/stop")
    
    def test_start_scheduler_invalid_interval(self, client):
        """잘못된 간격으로 스케줄러 시작 테스트"""
        # 간격이 범위를 벗어난 경우 (FastAPI가 자동으로 검증)
        response = client.post("/api/scheduler/start?interval_seconds=5")  # 최소 10초
        
        # FastAPI는 자동으로 검증하므로 422 또는 400
        assert response.status_code in [400, 422]
    
    def test_start_scheduler_already_running(self, client):
        """이미 실행 중인 스케줄러 재시작 테스트"""
        # 먼저 시작
        client.post("/api/scheduler/start")
        
        # 다시 시작 (재시작되어야 함)
        response = client.post("/api/scheduler/start")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["data"]["is_running"] is True
        
        # 정리
        client.post("/api/scheduler/stop")


class TestSchedulerStopAPI:
    """스케줄러 중지 API 테스트"""
    
    def test_stop_scheduler(self, client):
        """스케줄러 중지 테스트"""
        # 먼저 시작
        client.post("/api/scheduler/start")
        
        # 중지
        response = client.post("/api/scheduler/stop")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["data"]["is_running"] is False
        assert "Scheduler stopped successfully" in data["message"]
    
    def test_stop_scheduler_not_running(self, client):
        """실행 중이 아닌 스케줄러 중지 테스트"""
        # 먼저 중지 (확실히 중지 상태로)
        client.post("/api/scheduler/stop")
        
        # 다시 중지
        response = client.post("/api/scheduler/stop")
        
        # 중지 상태에서도 성공 응답을 반환해야 함
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["data"]["is_running"] is False


class TestSchedulerIntegration:
    """스케줄러 통합 테스트"""
    
    def test_scheduler_lifecycle(self, client, db_session):
        """스케줄러 생명주기 테스트"""
        # 종목 생성
        stock = Stock(ticker="SCHEDULER001", name="스케줄러 테스트", type="STOCK")
        db_session.add(stock)
        db_session.commit()
        
        # 1. 상태 조회 (중지 상태)
        response = client.get("/api/scheduler/status")
        assert response.status_code == 200
        status_data = response.json()["data"]
        initial_running = status_data["is_running"]
        
        # 2. 시작
        response = client.post("/api/scheduler/start?interval_seconds=30")
        assert response.status_code == 200
        assert response.json()["data"]["is_running"] is True
        
        # 3. 상태 조회 (실행 중)
        response = client.get("/api/scheduler/status")
        assert response.status_code == 200
        status_data = response.json()["data"]
        assert status_data["is_running"] is True
        assert status_data["interval_seconds"] == 30
        
        # 4. 중지
        response = client.post("/api/scheduler/stop")
        assert response.status_code == 200
        assert response.json()["data"]["is_running"] is False
        
        # 5. 상태 조회 (중지 상태)
        response = client.get("/api/scheduler/status")
        assert response.status_code == 200
        status_data = response.json()["data"]
        assert status_data["is_running"] is False

