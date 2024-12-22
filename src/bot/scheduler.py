import sys
import traceback
from logging import getLogger

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from src.bot.handlers import send_master_summaries
from src.bot.utils import notify_admin_on_error
from src.services.datetime_util import DatetimeUtil
from src.services.summarizer import (
    pull_articles_and_save_articles,
    create_and_save_summaries,
)

logger = getLogger(__name__)


def setup_article_pull_scheduler(bot_app):
    """Set up the scheduler and register tasks."""
    scheduler = AsyncIOScheduler()

    scheduler.add_job(
        pull_todays_articles,
        CronTrigger(
            hour=20, minute=00, timezone="UTC"
        ),  # Adjust time as needed, e.g. 'interval', minutes=5,
        kwargs={"bot_app": bot_app},
        id="daily_article_pull",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Article pull scheduler initialized and daily task scheduled at 8:00 PM UTC.")


def setup_summarize_scheduler(bot_app):
    """Set up the scheduler and register tasks."""
    scheduler = AsyncIOScheduler()

    scheduler.add_job(
        generate_master_summaries,
        CronTrigger(
            hour=3, minute=0, timezone="UTC"
        ),  # Adjust time as needed, e.g. 'interval', minutes=5,
        kwargs={"bot_app": bot_app},
        id="daily_summary",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Summarize scheduler initialized and daily task scheduled at 3:00 AM UTC.")


async def pull_todays_articles(bot_app):
    """Task to pull and save articles."""
    as_of_date = DatetimeUtil.utc_now().date()

    try:
        logger.info(f"Stage 1. Pulling articles and saving to db...")
        pull_articles_and_save_articles(as_of_date)
        logger.info("Successfully pulled and saved articles!\n\n")
    except Exception as e:
        exc_type, exc_value, exc_tb = sys.exc_info()
        tb_summary = traceback.extract_tb(exc_tb)

        error_message = f"Error occurred during daily scheduled process: {e}"
        messages = [error_message]
        logger.error(error_message)

        for tb in tb_summary:
            message = f"File: {tb.filename}, Line: {tb.lineno}, Function: {tb.name}, Code: {tb.line}"
            messages.append(message)
            logger.error(message)

        await notify_admin_on_error(bot_app.bot, "\n\n".join(messages))


async def generate_master_summaries(bot_app):
    """Task to generate master summaries."""
    as_of_date = DatetimeUtil.utc_yesterday().date()

    logger.info(f"Generating daily master summaries for {as_of_date}...")
    try:
        logger.info(
            f"Stage 2. Creating content summaries for every article for {as_of_date}. "
            f"Creating master summary for {as_of_date} per ticker..."
        )
        create_and_save_summaries(as_of_date)

        logger.info(
            f"Stage 3. Starting to send master summaries to each telegram group's topic..."
        )
        await send_master_summaries(as_of_date, bot_app)

        logger.info("Successfully sent daily master summaries!\n\n")
    except Exception as e:
        exc_type, exc_value, exc_tb = sys.exc_info()
        tb_summary = traceback.extract_tb(exc_tb)

        error_message = f"Error occurred during daily scheduled process: {e}"
        messages = [error_message]
        logger.error(error_message)

        for tb in tb_summary:
            message = f"File: {tb.filename}, Line: {tb.lineno}, Function: {tb.name}, Code: {tb.line}"
            messages.append(message)
            logger.error(message)

        await notify_admin_on_error(bot_app.bot, "\n\n".join(messages))
