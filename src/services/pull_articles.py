"""
This file contains functions to get/download/organize/save data from cryptonews websites.
"""

import datetime as dt
from logging import getLogger

import requests
from bs4 import BeautifulSoup

from src.config.config import app_settings
from src.database.database import save_articles_to_db
from src.database.models import CryptonewsArticlesDump
from src.services.utils import get_start_date

logger = getLogger(__name__)


def get_article_content(news_url: str) -> str:
    """
    Scrapes text of news article.
    """

    response = requests.get(news_url)
    page = response.text
    soup = BeautifulSoup(page, features="html.parser")

    try:
        article_content = soup.find(id="articleContent")
        if not article_content:
            article_content = soup.find(class_="post-box")
        if not article_content:
            article_content = soup.find(class_="entry-content")
    except:
        article_content = None

    return article_content.text if article_content else ""


def create_cryptonews_article_db_entity(
    metadata: dict,
    article_content: str,
    ticker: str,
) -> CryptonewsArticlesDump:
    """Create database entry."""

    date_str = metadata.get("date")
    datetime_obj = dt.datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z")

    # TODO: assign tags
    article = CryptonewsArticlesDump(
        news_url=metadata.get("news_url"),
        image_url=metadata.get("image_url"),
        title=metadata.get("title"),
        text=metadata.get("text"),
        source_name=metadata.get("source_name"),
        date=datetime_obj,
        topics=str(metadata.get("topics", "")),
        sentiment=metadata.get("sentiment"),
        content_type=metadata.get("type"),
        body=article_content,
        tags=ticker,
    )
    return article


def pull_articles(session, as_of_date: dt.date, ticker: str = None, test=False):
    """
    Collects all news articles according to tag as of previous business day through API and saves data to db.

    Tags feature is not available yet.
    """

    if test:
        pull_articles_stub(session, as_of_date)
    else:
        pull_articles_from_api(session, as_of_date, ticker)


def pull_articles_from_api(session, as_of_date: dt.date, ticker: str = None):
    """
    Collects all news articles according to tag as of previous business day through API and saves data to db.

    Tags feature is not available yet.
    """
    # Sundown Digest is an engaging evening article that encapsulates the crucial news and events of the day, presented in a digestible format. Available Mon-Fri at 7pm Eastern Time.
    # https://cryptonews-api.com/api/v1/sundown-digest?page=1&token=GET_API_KEY
    start_date = get_start_date(as_of_date)
    start_date_str = start_date.strftime("%m%d%Y")

    pages = 1
    items = 3  # 50
    token = app_settings.CRYPTONEWS_API_KEY

    # TODO: review timeframe set up in url
    # Available formats:
    #   01152019-today, 01152019-01152019, today, yesterday, last7days, last30days, yeartodate
    url_base = f"https://cryptonews-api.com"
    if ticker:
        url_with_params = f"{url_base}/api/v1?tickers={ticker}&items={items}&date={start_date_str}-today&token={token}"
    else:
        url_with_params = f"{url_base}/api/v1/category?section=general&items={items}&date={start_date_str}-today&token={token}"

    url_with_params_page1 = f"{url_with_params}&page=1"

    logger.info(
        f"Starting to pull data for {start_date.isoformat()} - {as_of_date.isoformat()} period from {url_base}..."
    )
    response = requests.get(f"{url_with_params}&page=1")
    if response and response.status_code != 200:
        raise Exception(response.content)
    response_json = response.json()
    articles_metadata_list = response_json.get("data", [])

    if not articles_metadata_list:
        logger.error(
            f"No data to pull from {url_with_params_page1}. Please check query parameters and date."
        )
        return

    db_entities = []
    # pages = response_json.get("total_pages", pages)
    for i in range(1, pages + 1):
        url_full = f"{url_with_params}&page={i}"
        response = requests.get(url_full)
        response_json = response.json()
        articles_metadata_list = response_json.get("data", [])

        for article_metadata in articles_metadata_list:
            news_url = article_metadata.get("news_url")
            if news_url:
                # TODO: do not scrape/save article's content, we have a article link saved and
                #  we can scrape it later if needed
                # article_content = get_article_content(news_url)
                article_content = ""
                db_entity = create_cryptonews_article_db_entity(
                    article_metadata, article_content, ticker
                )
                db_entities.append(db_entity)
    save_articles_to_db(session, db_entities)
    logger.info(
        f"Articles pull and save completed successfully. "
        f"Total number of saved articles: {len(db_entities)}.\n"
    )


def pull_articles_stub(session, as_of_date):
    as_of_date_str = as_of_date.isoformat()

    articles_metadata_list = [
        {
            "news_url": "https://cryptoslate.com/ftx-reorganizing-on-chain-assets-by-bridging-tokens-consolidating-holdings/",
            "image_url": "https://crypto.snapi.dev/images/v1/r/h/ftx-359381.jpg",
            "title": "FTX reorganizing on-chain assets by bridging tokens, consolidating holdings",
            "text": "Bankrupt crypto exchange FTX revealed in a tweet on Sept. 6 that it is in the process of moving its cryptocurrency holdings.",
            "source_name": "CryptoSlate",
            "date": as_of_date_str,
            "topics": [],
            "sentiment": "Neutral",
            "type": "Article",
        },
        {
            "news_url": "https://www.crypto-reporter.com/news/factors-for-a-profitable-cryptocurrency-investment-50333/",
            "image_url": "https://crypto.snapi.dev/images/v1/s/4/bitcoins-359375.jpg",
            "title": "Factors for a Profitable Cryptocurrency Investment",
            "text": "Currently, a lot of people want to invest in cryptocurrencies. However, before diving in, it's essential to consider several variables that can influence your investment decisions. Choosing the right cryptocurrency is crucial; you can opt for well-established ones, but they often require substantial financial commitments due to their high costs.",
            "source_name": "Crypto Reporter",
            "date": as_of_date_str,
            "topics": [],
            "sentiment": "Positive",
            "type": "Article",
        },
        {
            "news_url": "https://bitcoinworld.co.in/krafton-leaps-into-blockchain-with-settlus-a-game-changer-for-content-creators/?utm_source=snapi",
            "image_url": "https://crypto.snapi.dev/images/v1/r/3/krafton-se-450x300-359373.png",
            "title": "Krafton Leaps into Blockchain With Settlus: A Game-Changer for Content Creators?",
            "text": "Krafton, the South Korean video game giant best known for hits like PUBG: Battlegrounds, is stepping into the blockchain arena.",
            "source_name": "Bitcoinworld",
            "date": as_of_date_str,
            "topics": [],
            "sentiment": "Positive",
            "type": "Article",
        },
    ]
    db_entities = []
    for article_metadata in articles_metadata_list:
        news_url = article_metadata.get("news_url")
        article_content = get_article_content(news_url)
        db_entity = create_cryptonews_article_db_entity(
            article_metadata, article_content
        )
        db_entities.append(db_entity)
    save_articles_to_db(session, db_entities)
    logger.info("Completed.\n")
