import argparse
import datetime as dt

from loguru import logger

from src import create_content_summary, create_master_summary, download_articles
from src.database import create_session, CryptonewsArticlesDump

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--as_of_date')
    args = parser.parse_args()

    as_of_date = dt.datetime.strptime(args.as_of_date, "%Y-%m-%d") if args.as_of_date else dt.datetime.today()
    as_of_date = as_of_date.date()

    with create_session() as session:
        articles = session.query(CryptonewsArticlesDump).all()

        download_articles.pull_articles(session, as_of_date)
        create_content_summary.run(session, as_of_date)
        master_summary = create_master_summary.run(session, as_of_date)
        logger.info(f"\nHere is generated Sundown Digest as of {as_of_date.isoformat()}:\n\n{master_summary}")
