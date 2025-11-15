"""데이터베이스 Base 정의 (순환 import 방지)"""

from sqlalchemy.orm import declarative_base

# SQLAlchemy 2.0 스타일로 Base 생성
Base = declarative_base()

