import argparse
import datetime as dt

import streamlit as st

from src.utils import get_master_summary_file_path


def run(as_of_date: dt.date) -> str:
    f = open(get_master_summary_file_path(), "r")
    master_summary = f.read()
    st.write(
        f"""
    # Master Summary as of {as_of_date.isoformat()}
    {master_summary}
    """
    )
    return master_summary


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

    run(as_of_date)
