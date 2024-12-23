import datetime as dt
from logging import getLogger

from src.config.config import app_settings
from src.config.constants import TICKERS
from src.database.connection import create_session
from src.database.database import get_articles_by_ticker
from src.services.pull_articles import pull_articles
from src.services.utils import summarize_text

logger = getLogger(__name__)


def create_content_summary(session, as_of_date: dt.date, ticker: str):
    prompt = app_settings.CONTENT_SUMMARY_PROMPT
    logger.info(
        f"Starting content summary generation for each article with '{ticker}' ticker and no content summary.."
    )

    articles = get_articles_by_ticker(
        session, as_of_date, ticker, empty_content_summary=True
    )
    logger.info(
        f"Found {len(articles)} articles with '{ticker}' ticker and empty content summary. "
        f"LLM will be called for every link to summarize its content."
    )

    for article in articles:
        content_summary = summarize_text(article.news_url, prompt)
        article.content_summary = content_summary

    session.commit()
    logger.info("Content summary generation completed.\n")


def create_master_summary(session, as_of_date: dt.date, ticker: str):
    master_summary = ""
    prompt = app_settings.MASTER_SUMMARY_PROMPT
    logger.info(
        f"Starting master summary generation process for '{ticker}' ticker for all articles with content summary.."
    )

    # TODO: carefully select records based on date (take care of timezone)
    articles = get_articles_by_ticker(
        session,
        as_of_date,
        ticker,
        empty_content_summary=False,
        empty_master_summary=True,
    )
    logger.info(
        f"Found {len(articles)} articles with '{ticker}' ticker, not empty content summary and "
        f"empty master summary. LLM will be called for every link to summarize its content."
    )

    all_content_summaries_list = [article.content_summary for article in articles]
    all_content_summaries = "\n\n".join(all_content_summaries_list)

    if all_content_summaries:
        master_summary = articles[0].master_summary
        if not master_summary:
            master_summary = summarize_text(all_content_summaries, prompt)
            for article in articles:
                article.master_summary = master_summary
    else:
        logger.warning(f"No summaries were found for {as_of_date.isoformat()} date.")

    session.commit()
    logger.info("Master summary generation completed.\n")


def pull_articles_and_save_articles(as_of_date: dt.date, test: bool = False):
    """"""
    with create_session() as session:
        for ticker in TICKERS:
            logger.info(f"Starting articles pull for '{ticker}' ticker...")
            pull_articles(session, as_of_date, ticker, test=test)


def create_and_save_summaries(as_of_date: dt.date, test: bool = False):
    """"""
    with create_session() as session:
        for ticker in TICKERS:
            create_content_summary(session, as_of_date, ticker)

            create_master_summary(session, as_of_date, ticker)
