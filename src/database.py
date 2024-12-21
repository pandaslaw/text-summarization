import datetime as dt
from typing import List

from loguru import logger
from sqlalchemy import Integer, Date, and_, or_
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
    engine = create_engine(app_settings.DB_CONNECTION_STRING)
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


def get_articles_by_ticker(
    session,
    start_date: dt.date,
    ticker: str,
    empty_content_summary: bool = None,
    empty_master_summary: bool = None,
):
    """Load CryptonewsArticlesDump objects from database."""

    # TODO: carefully select records based on date (take care of timezone)
    all_conditions = [
        CryptonewsArticlesDump.date >= start_date,
        CryptonewsArticlesDump.tags == ticker,
    ]

    if empty_content_summary is not None:
        if empty_content_summary:
            content_summary_condition = or_(
                CryptonewsArticlesDump.content_summary.is_(None),
                CryptonewsArticlesDump.content_summary == "",
            )
        else:
            content_summary_condition = and_(
                CryptonewsArticlesDump.content_summary.isnot(None),
                CryptonewsArticlesDump.content_summary != "",
            )
        all_conditions.append(content_summary_condition)

    if empty_master_summary is not None:
        if empty_master_summary:
            master_summary_condition = or_(
                CryptonewsArticlesDump.master_summary.is_(None),
                CryptonewsArticlesDump.master_summary == "",
            )
        else:
            master_summary_condition = and_(
                CryptonewsArticlesDump.master_summary.isnot(None),
                CryptonewsArticlesDump.master_summary != "",
            )
        all_conditions.append(master_summary_condition)

    result = session.query(CryptonewsArticlesDump).filter(and_(*all_conditions)).all()
    return result


def get_master_summary(session, start_date: dt.date, ticker: str) -> str | None:
    """Load CryptonewsArticlesDump objects from database."""

    master_summary = (
        session.query(CryptonewsArticlesDump.master_summary)
        .filter(
            and_(
                CryptonewsArticlesDump.date == start_date,
                CryptonewsArticlesDump.tags == ticker,
            )
        )
        .first()
    )
    return master_summary[0] if master_summary else None


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
    engine = create_engine(app_settings.DB_CONNECTION_STRING)
    if drop_table:
        CryptonewsArticlesDump.__table__.drop(engine)

    logger.info("Create tables in the database (if they don't exist).")
    Base.metadata.create_all(engine)
    logger.info("Success.")


run(drop_table=False)
