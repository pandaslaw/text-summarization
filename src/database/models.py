from sqlalchemy import Integer, Date
from sqlalchemy import String
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import mapped_column

Base = declarative_base()


class CryptonewsArticlesDump(Base):
    __tablename__ = "cryptonews_articles_dump"

    id = mapped_column(Integer, primary_key=True)
    news_url = mapped_column(String, nullable=False)
    image_url = mapped_column(String, nullable=True)
    title = mapped_column(String, nullable=False)
    text = mapped_column(String, nullable=True)
    source_name = mapped_column(String, nullable=True)
    date = mapped_column(Date, nullable=True)
    topics = mapped_column(String, nullable=True)
    sentiment = mapped_column(String, nullable=True)
    content_type = mapped_column(String, nullable=True)
    body = mapped_column(String, nullable=True)
    content_summary = mapped_column(String, nullable=True)
    master_summary = mapped_column(String, nullable=True)
    tags = mapped_column(String, nullable=True)
