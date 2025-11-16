"""
스케줄러 관리 API 라우터

데이터 수집 스케줄러의 상태 조회 및 제어를 제공합니다.
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from typing import Optional

from app.scheduler.data_scheduler import get_scheduler
from app.schemas.response import APIResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/status", response_model=APIResponse)
async def get_scheduler_status():
    """
    스케줄러 상태 조회 API
    
    현재 스케줄러의 실행 상태, 다음 실행 시간, 마지막 실행 결과 등을 조회합니다.
    
    **Example Response:**
    ```json
    {
      "success": true,
      "data": {
        "is_running": true,
        "interval_seconds": 30,
        "next_run_time": "2025-11-14T10:30:30",
        "last_run_time": "2025-11-14T10:30:00",
        "last_run_status": "success",
        "last_run_error": null
      },
      "message": "Scheduler status retrieved successfully",
      "timestamp": "2025-11-14T10:30:05"
    }
    ```
    
    **Status Codes:**
    - 200: 성공
    - 500: 서버 오류
    """
    try:
        scheduler = get_scheduler()
        status = scheduler.get_status()
        
        return APIResponse(
            success=True,
            data=status,
            message="Scheduler status retrieved successfully",
            timestamp=datetime.now(),
        )
    
    except Exception as e:
        logger.error(f"Error getting scheduler status: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get scheduler status: {str(e)}"
        )


@router.post("/start", response_model=APIResponse)
async def start_scheduler(
    interval_seconds: Optional[int] = Query(
        None, 
        ge=10, 
        le=3600, 
        description="데이터 수집 간격 (초 단위, 기본: 30초, 최소: 10초, 최대: 3600초)"
    ),
):
    """
    스케줄러 시작 API
    
    데이터 수집 스케줄러를 시작합니다. 이미 실행 중인 경우 재시작합니다.
    
    - **interval_seconds**: 데이터 수집 간격 (초 단위, 선택사항, 기본: 30초)
    
    **Example Request:**
    ```
    POST /api/scheduler/start?interval_seconds=30
    ```
    
    **Example Response:**
    ```json
    {
      "success": true,
      "data": {
        "is_running": true,
        "interval_seconds": 30,
        "message": "Scheduler started successfully"
      },
      "message": "Scheduler started successfully",
      "timestamp": "2025-11-14T10:30:00"
    }
    ```
    
    **Status Codes:**
    - 200: 성공
    - 500: 서버 오류
    """
    try:
        scheduler = get_scheduler()
        
        # 간격이 지정된 경우 새로 생성
        if interval_seconds is not None:
            # 기존 스케줄러 중지
            if scheduler.is_running:
                scheduler.stop()
            
            # 새 스케줄러 생성
            from app.scheduler.data_scheduler import DataScheduler
            import app.scheduler.data_scheduler as scheduler_module
            scheduler_module._scheduler_instance = DataScheduler(interval_seconds=interval_seconds)
            scheduler = scheduler_module._scheduler_instance
        
        # 스케줄러 시작
        scheduler.start()
        
        logger.info(f"Scheduler started via API (interval: {scheduler.interval_seconds}s)")
        
        return APIResponse(
            success=True,
            data={
                "is_running": scheduler.is_running,
                "interval_seconds": scheduler.interval_seconds,
                "message": "Scheduler started successfully"
            },
            message="Scheduler started successfully",
            timestamp=datetime.now(),
        )
    
    except Exception as e:
        logger.error(f"Error starting scheduler: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start scheduler: {str(e)}"
        )


@router.post("/stop", response_model=APIResponse)
async def stop_scheduler():
    """
    스케줄러 중지 API
    
    실행 중인 데이터 수집 스케줄러를 중지합니다.
    
    **Example Request:**
    ```
    POST /api/scheduler/stop
    ```
    
    **Example Response:**
    ```json
    {
      "success": true,
      "data": {
        "is_running": false,
        "message": "Scheduler stopped successfully"
      },
      "message": "Scheduler stopped successfully",
      "timestamp": "2025-11-14T10:30:00"
    }
    ```
    
    **Status Codes:**
    - 200: 성공
    - 500: 서버 오류
    """
    try:
        scheduler = get_scheduler()
        scheduler.stop()
        
        logger.info("Scheduler stopped via API")
        
        return APIResponse(
            success=True,
            data={
                "is_running": scheduler.is_running,
                "message": "Scheduler stopped successfully"
            },
            message="Scheduler stopped successfully",
            timestamp=datetime.now(),
        )
    
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to stop scheduler: {str(e)}"
        )

