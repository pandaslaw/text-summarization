"""
Creates content summary for each article within previous business day for all db records
with no content summary and updates db records with generated content summary.
"""

import argparse
import datetime as dt

from loguru import logger

from src.config import app_settings
from src.database import create_session, get_articles_by_summary
from src.summarization.utils.utils import get_start_date, summarize_text


def run(session, as_of_date: dt.date):
    prompt = app_settings.PROMPT_FOR_CONTENT_SUMMARY
    start_date = get_start_date(as_of_date)
    logger.info(
        "Starting summary generation process for each article with no content summary.."
    )

    articles = get_articles_by_summary(session, start_date, empty_summary=True)

    for article in articles:
        content_summary = summarize_text(article.body, prompt)
        article.content_summary = content_summary

    session.commit()
    logger.info("Completed.\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--as_of_date")
    args = parser.parse_args()

    as_of_date = (
        dt.datetime.strptime(args.as_of_date, "%Y-%m-%d")
        if args.as_of_date
        else dt.datetime.today()
    )
    as_of_date = as_of_date.date()

    with create_session() as session:
        run(session, as_of_date)
