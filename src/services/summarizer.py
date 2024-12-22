import datetime as dt
from logging import getLogger

from src.config.config import app_settings
from src.config.constants import TICKERS
from src.database.connection import create_session
from src.database.database import get_articles_by_ticker, get_master_summary
from src.services.pull_articles import pull_articles
from src.services.utils import get_start_date, summarize_text

logger = getLogger(__name__)


def create_content_summary(session, as_of_date: dt.date, ticker: str):
    prompt = app_settings.CONTENT_SUMMARY_PROMPT
    start_date = get_start_date(as_of_date)
    logger.info(
        "Starting summary generation process for each article with no content summary.."
    )

    articles = get_articles_by_ticker(
        session, start_date, ticker, empty_content_summary=True
    )

    for article in articles:
        content_summary = summarize_text(article.news_url, prompt)
        article.content_summary = content_summary

    session.commit()
    logger.info("Completed.\n")


def create_master_summary(session, as_of_date: dt.date, ticker: str) -> str:
    master_summary = ""
    prompt = app_settings.MASTER_SUMMARY_PROMPT
    start_date = get_start_date(as_of_date)
    logger.info(
        "Starting master summary generation process for all article with content summary.."
    )

    # TODO: carefully select records based on date (take care of timezone)
    articles = get_articles_by_ticker(
        session,
        start_date,
        ticker,
        empty_content_summary=False,
        empty_master_summary=True,
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
        logger.warning(f"No summaries were found for {start_date.isoformat()} date.")

    session.commit()
    logger.info("Completed.\n")
    return master_summary


def pull_articles_and_save_articles(as_of_date: dt.date, test: bool = False):
    """"""
    with create_session() as session:
        for ticker in TICKERS:
            pull_articles(session, as_of_date, ticker, test=test)


def create_and_save_summaries(as_of_date: dt.date, test: bool = False) -> str:
    """"""
    with create_session() as session:
        for ticker in TICKERS:
            create_content_summary(session, as_of_date, ticker)

            master_summary = create_master_summary(session, as_of_date, ticker)

        master_summary = get_master_summary(session, as_of_date, "BTC")
        logger.info(
            f"\nHere is generated Sundown Digest as of {as_of_date.isoformat()}:\n\n{master_summary}"
        )
        return master_summary
