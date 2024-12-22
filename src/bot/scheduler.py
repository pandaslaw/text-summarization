from logging import getLogger

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from src.bot.admin_handlers import notify_admin_on_error
from src.bot.handlers import send_master_summaries
from src.services.datetime_util import DatetimeUtil
from src.services.summarizer import (
    pull_articles_and_save_articles,
    create_and_save_summaries,
)

logger = getLogger(__name__)


def setup_scheduler(app):
    """Set up the scheduler and register tasks."""
    scheduler = AsyncIOScheduler()

    # Schedule daily summary generation
    scheduler.add_job(
        generate_master_summaries,
        CronTrigger(
            hour=3, minute=0, timezone="UTC"
        ),  # Adjust time as needed, e.g. 'interval', minutes=5,
        kwargs={"bot_app": app},
        id="daily_summary",
        replace_existing=True,
    )

    # Start the scheduler
    scheduler.start()
    logger.info("Scheduler initialized and daily task scheduled at 3:00 AM UTC.")


async def generate_master_summaries(bot_app):
    """Task to generate master summaries."""
    as_of_date = DatetimeUtil.utc_yesterday().date()

    logger.info(f"Generating daily master summaries for {as_of_date}...")
    try:
        logger.info(f"Stage 1. Pulling articles and saving to db...")
        pull_articles_and_save_articles(as_of_date)

        logger.info(
            f"Stage 3. Creating content summaries for every article for {as_of_date}. "
            f"Creating master summary for {as_of_date} per ticker..."
        )
        create_and_save_summaries(as_of_date)

        logger.info(
            f"Stage 3. Starting to send master summaries to each telegram group's topic..."
        )
        await send_master_summaries(as_of_date)

        logger.info("Successfully sent daily master summaries!")
    except Exception as e:
        logger.error(f"Error generating summaries: {e}")
        await notify_admin_on_error(
            bot_app.bot, f"Failed to generate daily summaries: {e}"
        )
