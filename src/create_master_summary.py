"""
Creates master summary based on all articles within previous business day
and updates master_summary field of each db record with the generated summary.
"""

import argparse
import datetime as dt

from loguru import logger
from sqlalchemy import and_

from src.config import app_settings
from src.database import create_session, CryptonewsArticlesDump
from src.utils import generate_summary, get_start_date


def run(session, as_of_date: dt.date) -> str:
    master_summary = ""
    prompt = app_settings.PROMPT_FOR_MASTER_SUMMARY
    start_date = get_start_date(as_of_date)
    logger.info("Starting master summary generation process for all article with content summary..")

    # TODO: carefully select records based on date (take care of timezone)
    articles = session.query(CryptonewsArticlesDump).filter(
        and_(CryptonewsArticlesDump.date >= start_date, CryptonewsArticlesDump.content_summary != None)).all()

    all_content_summaries_list = [article.content_summary for article in articles]
    all_content_summaries = "\n".join(all_content_summaries_list)

    if all_content_summaries:
        master_summary = articles[0].master_summary
        if not master_summary:
            master_summary = generate_summary(all_content_summaries, prompt)
            for article in articles:
                article.master_summary = master_summary
    else:
        logger.warning(f"No summaries were found for {start_date.isoformat()} date.")

    session.commit()
    logger.info("Completed.\n")
    return master_summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--as_of_date')
    args = parser.parse_args()

    as_of_date = dt.datetime.strptime(args.as_of_date, "%Y-%m-%d") if args.as_of_date else dt.datetime.today()
    as_of_date = as_of_date.date()

    with create_session() as session:
        articles = session.query(CryptonewsArticlesDump).all()
        run(session, as_of_date)
