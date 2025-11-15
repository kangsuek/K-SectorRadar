"""가격 데이터 모델"""

from sqlalchemy import Column, BigInteger, Integer, String, Numeric, DateTime, Date, ForeignKey, Index
from sqlalchemy.sql import func
from datetime import datetime

from app.db_base import Base
from app.db_types import AutoIncrementBigInteger


class Price(Base):
    """가격 데이터 테이블"""

    __tablename__ = "prices"

    id = Column(AutoIncrementBigInteger, primary_key=True, autoincrement=True, comment="고유 ID")
    ticker = Column(String(10), ForeignKey("stocks.ticker", ondelete="CASCADE"), nullable=False, comment="종목 코드")
    date = Column(Date, nullable=False, comment="거래일")
    timestamp = Column(DateTime, nullable=False, comment="수집 시각")
    current_price = Column(Numeric(12, 2), nullable=False, comment="현재가")
    change_rate = Column(Numeric(6, 2), nullable=True, comment="등락률 (%)")
    change_amount = Column(Numeric(12, 2), nullable=True, comment="등락액")
    open_price = Column(Numeric(12, 2), nullable=True, comment="시가")
    high_price = Column(Numeric(12, 2), nullable=True, comment="고가")
    low_price = Column(Numeric(12, 2), nullable=True, comment="저가")
    volume = Column(Numeric(20, 0), nullable=True, comment="거래량")
    weekly_change_rate = Column(Numeric(6, 2), nullable=True, comment="주간 등락률 (%)")
    previous_close = Column(Numeric(12, 2), nullable=True, comment="전일 종가")

    __table_args__ = (
        Index("idx_price_ticker_date", "ticker", "date"),
        Index("idx_price_ticker_timestamp", "ticker", "timestamp"),
    )

    def __repr__(self):
        return f"<Price(ticker={self.ticker}, date={self.date}, price={self.current_price})>"

