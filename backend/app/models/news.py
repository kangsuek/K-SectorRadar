"""뉴스 데이터 모델"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Index, UniqueConstraint
from datetime import datetime

from app.db_base import Base


class News(Base):
    """뉴스 테이블"""

    __tablename__ = "news"

    id = Column(String(50), primary_key=True, comment="고유 ID")
    ticker = Column(String(10), ForeignKey("stocks.ticker", ondelete="CASCADE"), nullable=False, comment="관련 종목 코드")
    title = Column(String(500), nullable=False, comment="뉴스 제목")
    url = Column(String(1000), nullable=False, comment="뉴스 URL")
    source = Column(String(100), nullable=True, comment="출처")
    published_at = Column(DateTime, nullable=True, comment="발행 시각")
    collected_at = Column(DateTime, nullable=False, default=datetime.utcnow, comment="수집 시각")

    __table_args__ = (
        Index("idx_news_ticker_published", "ticker", "published_at"),
        Index("idx_news_published_at", "published_at"),
        UniqueConstraint("url", name="uk_news_url"),
    )

    def __repr__(self):
        return f"<News(id={self.id}, ticker={self.ticker}, title={self.title[:50]})>"

