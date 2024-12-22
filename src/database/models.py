import uuid

from sqlalchemy import Date, func, DateTime, Text, UniqueConstraint, UUID, ARRAY
from sqlalchemy import String
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import mapped_column

Base = declarative_base()


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
    master_summary = mapped_column(Text, nullable=True)  # LLM summary of the list of content summaries for the ticker and as_of_date

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
