import datetime as dt
from logging import getLogger
from typing import List

from sqlalchemy import and_, or_

from src.database.models import CryptonewsArticlesDump

logger = getLogger(__name__)


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


from sqlalchemy.orm import joinedload

articles = session.query(CryptonewsArticle).options(joinedload(CryptonewsArticle.master_summary)).all()
for article in articles:
    print(f"Article: {article.title}, Summary: {article.master_summary.summary_text if article.master_summary else 'No summary'}")

def get_or_create_master_summary(session, ticker, as_of_date):
    summary = session.query(MasterSummary).filter_by(ticker=ticker, as_of_date=as_of_date).first()
    if not summary:
        summary = MasterSummary(ticker=ticker, as_of_date=as_of_date)
        session.add(summary)
    return summary


# Example: Adding topics and tickers
article = CryptonewsArticle(news_url="example.com", title="Sample Title", published_at=datetime.utcnow())

# Add topics
topic1 = session.query(Topic).filter_by(name="pricemovement").first() or Topic(name="pricemovement")
topic2 = session.query(Topic).filter_by(name="markettrend").first() or Topic(name="markettrend")
article.topics.extend([topic1, topic2])

# Add tickers
ticker1 = session.query(Ticker).filter_by(symbol="BTC").first() or Ticker(symbol="BTC")
ticker2 = session.query(Ticker).filter_by(symbol="USDC").first() or Ticker(symbol="USDC")
article.tickers.extend([ticker1, ticker2])

session.add(article)
session.commit()

# Fetch all articles related to a specific topic
topic = session.query(Topic).filter_by(name="pricemovement").first()
if topic:
    for article in topic.articles:
        print(article.title)

# Fetch all articles related to a specific ticker
ticker = session.query(Ticker).filter_by(symbol="BTC").first()
if ticker:
    for article in ticker.articles:
        print(article.title)

