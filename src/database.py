import datetime as dt
from typing import List

from loguru import logger
from sqlalchemy import Integer, Date, and_
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
    date = mapped_column(Date, nullable=True)
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


def get_articles(session, start_date: dt.date = None) -> List[CryptonewsArticlesDump]:
    """Load CryptonewsArticlesDump objects from database."""

    if start_date:
        return (
            session.query(CryptonewsArticlesDump)
            .filter(CryptonewsArticlesDump.date >= start_date)
            .all()
        )
    return session.query(CryptonewsArticlesDump).all()


def get_articles_by_summary(session, start_date: dt.date, empty_summary: bool = True):
    """Load CryptonewsArticlesDump objects from database."""

    # TODO: carefully select records based on date (take care of timezone)
    contrent_summary_condition = (
        CryptonewsArticlesDump.content_summary != None
        if not empty_summary
        else CryptonewsArticlesDump.content_summary == None
    )
    return (
        session.query(CryptonewsArticlesDump)
        .filter(
            and_(CryptonewsArticlesDump.date >= start_date, contrent_summary_condition)
        )
        .all()
    )


def save_articles_to_db(session, cryptonews_articles: List[CryptonewsArticlesDump]):
    """Insert list of CryptonewsArticlesDump objects to database."""

    for article in cryptonews_articles:
        q = session.query(CryptonewsArticlesDump.id).filter(
            CryptonewsArticlesDump.news_url == article.news_url
        )
        is_already_in_db = session.query(q.exists()).scalar()
        if not is_already_in_db:
            session.add(article)
    session.commit()


def run(drop_table: bool = False):
    engine = create_engine(app_settings.DATABASE_URL)
    if drop_table:
        CryptonewsArticlesDump.__table__.drop(engine)

    logger.info("Create tables in the database (if they don't exist).")
    Base.metadata.create_all(engine)
    logger.info("Success.")


run(drop_table=False)
