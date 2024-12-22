"""
Creates content summary for each article within previous business day for all db records
with no content summary and updates db records with generated content summary.
"""

import argparse
import datetime as dt

from src.database.connection import create_session
from src.services.summarizer import create_content_summary

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--as_of_date")
    parser.add_argument("--ticker")
    args = parser.parse_args()

    as_of_date = (
        dt.datetime.strptime(args.as_of_date, "%Y-%m-%d")
        if args.as_of_date
        else dt.datetime.today()
    )
    as_of_date = as_of_date.date()
    ticker = args.ticker

    with create_session() as session:
        create_content_summary(session, as_of_date, ticker)
