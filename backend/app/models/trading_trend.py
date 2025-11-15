"""매매 동향 모델"""

from sqlalchemy import Column, BigInteger, Integer, String, Numeric, DateTime, Date, ForeignKey, Index
from datetime import datetime

from app.db_base import Base


class TradingTrend(Base):
    """매매 동향 테이블"""

    __tablename__ = "trading_trends"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="고유 ID")
    ticker = Column(String(10), ForeignKey("stocks.ticker", ondelete="CASCADE"), nullable=False, comment="종목 코드")
    date = Column(Date, nullable=False, comment="거래일")
    timestamp = Column(DateTime, nullable=False, comment="수집 시각")
    individual = Column(Numeric(20, 0), nullable=True, comment="개인 투자자 거래량 (순매수: +, 순매도: -)")
    institution = Column(Numeric(20, 0), nullable=True, comment="기관 투자자 거래량")
    foreign_investor = Column(Numeric(20, 0), nullable=True, comment="외국인 투자자 거래량")
    total = Column(Numeric(20, 0), nullable=True, comment="총 거래량")

    __table_args__ = (
        Index("idx_trading_ticker_date", "ticker", "date"),
        Index("idx_trading_ticker_timestamp", "ticker", "timestamp"),
    )

    def __repr__(self):
        return f"<TradingTrend(ticker={self.ticker}, date={self.date})>"

