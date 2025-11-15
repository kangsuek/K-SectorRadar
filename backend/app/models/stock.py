"""주식 정보 모델"""

from sqlalchemy import Column, String, Numeric, DateTime, CheckConstraint, Index
from sqlalchemy.sql import func
from datetime import datetime

from app.db_base import Base


class Stock(Base):
    """주식 정보 테이블"""

    __tablename__ = "stocks"

    ticker = Column(String(10), primary_key=True, comment="종목 코드")
    name = Column(String(100), nullable=False, comment="종목명")
    type = Column(String(10), nullable=False, comment="종목 유형 (STOCK/ETF)")
    theme = Column(String(200), nullable=True, comment="테마 분류")
    fee = Column(Numeric(10, 6), nullable=True, comment="수수료 (ETF만 해당)")
    created_at = Column(DateTime, default=func.now(), nullable=False, comment="생성일시")
    updated_at = Column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="수정일시",
    )

    __table_args__ = (
        CheckConstraint("type IN ('STOCK', 'ETF')", name="check_stock_type"),
        Index("idx_stock_type", "type"),
        Index("idx_stock_theme", "theme"),
    )

    def __repr__(self):
        return f"<Stock(ticker={self.ticker}, name={self.name}, type={self.type})>"

