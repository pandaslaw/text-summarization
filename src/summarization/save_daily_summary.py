import datetime as dt
from logging import getLogger

from src.constants import TICKERS
from src.database import create_session, get_master_summary
from src.scraping import download_articles
from src.summarization import create_content_summary, create_master_summary

logger = getLogger(__name__)


def pull_articles_and_save_articles(as_of_date: dt.date, test: bool = False):
    """"""
    with create_session() as session:
        for ticker in TICKERS:
            download_articles.pull_articles(session, as_of_date, ticker, test=test)


def create_and_save_summaries(as_of_date: dt.date, test: bool = False) -> str:
    """"""
    with create_session() as session:
        for ticker in TICKERS:
            create_content_summary.run(session, as_of_date, ticker)

            master_summary = create_master_summary.run(session, as_of_date, ticker)

        master_summary = get_master_summary(session, as_of_date, "BTC")
        logger.info(
            f"\nHere is generated Sundown Digest as of {as_of_date.isoformat()}:\n\n{master_summary}"
        )
        return master_summary
