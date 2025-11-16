"""애플리케이션 설정"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Union
import json


class Settings(BaseSettings):
    """애플리케이션 설정"""

    # Database - MySQL only (required)
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/sectorradar"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True

    # CORS - 쉼표로 구분된 문자열 또는 JSON 배열 형식 지원
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:5173,http://localhost:3000"
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """CORS_ORIGINS 환경 변수 파싱"""
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            # JSON 형식인 경우
            if v.strip().startswith('[') and v.strip().endswith(']'):
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    pass
            # 쉼표로 구분된 문자열인 경우
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra='ignore',  # .env 파일에 정의되지 않은 필드 무시
    )

    # Data Collection
    AUTO_REFRESH_INTERVAL: int = 30
    NAVER_FINANCE_BASE_URL: str = "https://finance.naver.com"
    NAVER_NEWS_BASE_URL: str = "https://search.naver.com"

    # Logging
    LOG_LEVEL: str = "INFO"

    # Environment
    ENVIRONMENT: str = "development"


settings = Settings()

