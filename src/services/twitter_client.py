import asyncio
from datetime import datetime, timedelta
from logging import getLogger

import tweepy

from src.config.config import app_settings
from src.services.utils import summarize_text

# Set up logging
logger = getLogger(__name__)

# Initialize Tweepy client
client = tweepy.Client(
    bearer_token=app_settings.TWITTER_BEARER_TOKEN,
    consumer_key=app_settings.TWITTER_API_KEY,
    consumer_secret=app_settings.TWITTER_API_SECRET_KEY,
    access_token=app_settings.TWITTER_ACCESS_TOKEN,
    access_token_secret=app_settings.TWITTER_ACCESS_TOKEN_SECRET,
)


async def fetch_tweets(account_handle: str, since: datetime, until: datetime):
    """
    Fetch tweets from a specific account within a date range.
    """
    try:
        tweets = client.get_users_tweets(
            id=client.get_user(username=account_handle).data.id,
            start_time=since.isoformat() + "Z",
            end_time=until.isoformat() + "Z",
            tweet_fields=["created_at", "text"],
            max_results=100,
        )
        return [tweet.text for tweet in tweets.data] if tweets.data else []
    except Exception as e:
        logger.error(f"Failed to fetch tweets: {e}")
        return []


async def summarize_tweets(tweets):
    """
    Summarize a list of tweets using GPT.
    """
    if not tweets:
        return "No tweets available to summarize for today."

    prompt = "Summarize the following tweets into a brief daily summary"
    tweets_text = "\n\n".join(tweets)

    try:
        content_summary = summarize_text(tweets_text, prompt)
        return content_summary
    except Exception as e:
        logger.error(f"Failed to summarize tweets: {e}")
        return "Could not generate a summary."


async def generate_daily_twitter_summary():
    """
    Fetch and summarize daily tweets from a specific account.
    """
    today = datetime.utcnow()
    yesterday = today - timedelta(days=1)

    account_handle = "storyprotocol"  # https://x.com/StoryProtocol

    logger.info("Fetching tweets for summarization...")
    tweets = await fetch_tweets(account_handle, since=yesterday, until=today)

    logger.info(f"Fetched {len(tweets)} tweets. Generating summary...")
    summary = await summarize_tweets(tweets)

    logger.info(f"Generated summary: {summary}")
    return summary


async def send_twitter_summary_to_telegram(summary):
    """
    Send the Twitter summary to a Telegram channel or user.
    """
    # Replace this with your Telegram bot sending logic
    logger.info(f"Sending summary to Telegram:\n{summary}")


async def run_twitter_summarizer():
    """
    Main function to generate and send the daily Twitter summary.
    """
    summary = await generate_daily_twitter_summary()
    await send_twitter_summary_to_telegram(summary)


if __name__ == "__main__":
    asyncio.run(run_twitter_summarizer())
