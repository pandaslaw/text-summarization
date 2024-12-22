"""
Creates master summary based on all articles within previous business day
and updates master_summary field of each db record with the generated summary.
"""

import argparse
import datetime as dt

from src.database.connection import create_session
from src.services.summarizer import create_master_summary

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
        create_master_summary(session, as_of_date, ticker)
