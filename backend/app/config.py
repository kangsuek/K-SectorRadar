"""애플리케이션 설정"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """애플리케이션 설정"""

    # Database
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/sectorradar"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Data Collection
    AUTO_REFRESH_INTERVAL: int = 30
    NAVER_FINANCE_BASE_URL: str = "https://finance.naver.com"
    NAVER_NEWS_BASE_URL: str = "https://search.naver.com"

    # Logging
    LOG_LEVEL: str = "INFO"

    # Environment
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

