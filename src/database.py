from loguru import logger
from sqlalchemy import Integer, DateTime
from sqlalchemy import String
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import sessionmaker

from src.config import app_settings

Base = declarative_base()


class CryptonewsArticlesDump(Base):
    __tablename__ = "cryptonews_articles_dump"

    id = mapped_column(Integer, primary_key=True)
    news_url = mapped_column(String, nullable=False)
    image_url = mapped_column(String, nullable=True)
    title = mapped_column(String, nullable=False)
    text = mapped_column(String, nullable=True)
    source_name = mapped_column(String, nullable=True)
    date = mapped_column(DateTime, nullable=True)
    topics = mapped_column(String, nullable=True)
    sentiment = mapped_column(String, nullable=True)
    content_type = mapped_column(String, nullable=True)
    body = mapped_column(String, nullable=True)
    content_summary = mapped_column(String, nullable=True)
    master_summary = mapped_column(String, nullable=True)
    tags = mapped_column(String, nullable=True)


def create_session():
    engine = create_engine(app_settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    return Session()


def run():
    engine = create_engine(app_settings.DATABASE_URL)
    # CryptonewsArticlesDump.__table__.drop(engine)

    logger.info("Create tables in the database (if they don't exist).")
    Base.metadata.create_all(engine)
    logger.info("Success.")


if __name__ == "__main__":
    run()
