from logging import getLogger

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

logger = getLogger(__name__)


def setup_scheduler(app):
    """Set up the scheduler and register tasks."""
    scheduler = AsyncIOScheduler()

    # Schedule daily summary generation
    scheduler.add_job(
        generate_master_summaries,
        CronTrigger(hour=23, minute=59),  # Adjust time as needed
        kwargs={"bot_app": app},
        id="daily_summary",
        replace_existing=True,
    )

    # Start the scheduler
    scheduler.start()
    logger.info("Scheduler initialized.")
