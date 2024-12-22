import uuid

from sqlalchemy import Date, func, DateTime, Text, UniqueConstraint, UUID, ARRAY, Table
from sqlalchemy import String
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import mapped_column
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, UniqueConstraint, func
from sqlalchemy.orm import relationship
Base = declarative_base()

# Association tables
article_topic_association = Table(
    'article_topic_association', Base.metadata,
    Column('article_id', ForeignKey('cryptonews_articles.id'), primary_key=True),
    Column('topic_id', ForeignKey('topics.id'), primary_key=True)
)

article_ticker_association = Table(
    'article_ticker_association', Base.metadata,
    Column('article_id', ForeignKey('cryptonews_articles.id'), primary_key=True),
    Column('ticker_id', ForeignKey('tickers.id'), primary_key=True)
)

class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

class Ticker(Base):
    __tablename__ = "tickers"

    id = Column(Integer, primary_key=True)
    symbol = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

class MasterSummary(Base):
    __tablename__ = "master_summaries"

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    as_of_date = mapped_column(Date, nullable=False)
    ticker = mapped_column(String, nullable=False)
    summary = mapped_column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint('as_of_date', 'ticker', name='unique_summary_per_ticker_date'),
    )

class CryptonewsArticle(Base):
    __tablename__ = "cryptonews_articles"

    # Primary Key
    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Article Metadata
    news_url = mapped_column(String, nullable=False, unique=True)  # Ensure each article is unique by URL.
    image_url = mapped_column(String, nullable=True)
    title = mapped_column(String, nullable=False)
    source_name = mapped_column(String, nullable=True)

    # Article Content
    text = mapped_column(Text, nullable=True)
    body = mapped_column(Text, nullable=True)
    content_summary = mapped_column(Text, nullable=True)  # LLM summary of the body.
    master_summary_id = Column(Integer, ForeignKey('master_summaries.id'), nullable=True)

    # Article Attributes
    as_of_date = mapped_column(DateTime, nullable=True)
    topics = mapped_column(ARRAY(String), nullable=True)  # Store topics as an array for flexibility.
    sentiment = mapped_column(String, nullable=True)
    content_type = mapped_column(String, nullable=True)
    tickers = mapped_column(ARRAY(String), nullable=True)  # Rename `tags` to `tickers` for clarity.

    # Timestamps
    created_at = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)

    # Unique Constraints
    __table_args__ = (
        UniqueConstraint('news_url', 'as_of_date', name='unique_article_per_date'),
    )

    # Relationships
    master_summary = relationship("MasterSummary", back_populates="articles")
    topics = relationship("Topic", secondary=article_topic_association, back_populates="articles")
    tickers = relationship("Ticker", secondary=article_ticker_association, back_populates="articles")


# Define relationship in MasterSummary
MasterSummary.articles = relationship("CryptonewsArticle", back_populates="master_summary")
# Add reverse relationships in Topic and Ticker
Topic.articles = relationship("CryptonewsArticle", secondary=article_topic_association, back_populates="topics")
Ticker.articles = relationship("CryptonewsArticle", secondary=article_ticker_association, back_populates="tickers")