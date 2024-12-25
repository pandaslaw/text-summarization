import argparse
import datetime as dt
import json
import os
from logging import getLogger

import streamlit as st

from src.config import app_settings
from src.summarization.utils.utils import (
    get_master_summary_file_path,
    summarize_text,
)

logger = getLogger(__name__)


def run(as_of_date: dt.date, data_source_file_name: str = None) -> str:
    if data_source_file_name and data_source_file_name.endswith(".json"):
        header = f"Master Summary of {data_source_file_name} file's content:"

        path_to_data_source_files = os.path.join(os.path.abspath(os.curdir), "data")
        full_path = os.path.join(path_to_data_source_files, data_source_file_name)
        logger.info(f"Trying to load data from '{full_path}' file..")
        with open(full_path) as f:
            articles = json.load(f)

        prompt = app_settings.MASTER_SUMMARY_PROMPT

        all_content_summaries_list = [
            article["body"] for article in articles if article.get("body")
        ]
        all_content_summaries = "\n\n".join(all_content_summaries_list)
        logger.info(
            f"Total articles in '{full_path}' file: {len(articles)}. "
            f"Articles with body: {len(all_content_summaries_list)}."
        )

        master_summary = ""
        if all_content_summaries:
            logger.info(f"Starting summary generation process for all articles..")
            master_summary = summarize_text(all_content_summaries, prompt)
            logger.info("Completed.")
    else:
        header = f"Master Summary as of {as_of_date.isoformat()}"
        with open(get_master_summary_file_path(), "r") as f:
            master_summary = f.read()
    st.write(
        f"""
        # {header}
        {master_summary}
        """
    )
    return master_summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--as_of_date")
    parser.add_argument("--data_source_file_name")
    args = parser.parse_args()

    as_of_date = (
        dt.datetime.strptime(args.as_of_date, "%Y-%m-%d")
        if args.as_of_date
        else dt.datetime.today()
    )
    as_of_date = as_of_date.date()
    data_source_file_name = args.data_source_file_name

    run(as_of_date, data_source_file_name)
