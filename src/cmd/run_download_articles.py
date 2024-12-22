"""
This file contains functions to get/download/organize/save data from cryptonews websites.
"""

import argparse
import datetime as dt
from logging import getLogger

from src.database.connection import create_session
from src.services.pull_articles import pull_articles

logger = getLogger(__name__)

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
        pull_articles(session, as_of_date, test=False)
