import argparse
import asyncio
import datetime as dt
from logging import getLogger

from src.bot.handlers.summary_handler import send_master_summaries
from telegram import Bot
from telegram.ext import ApplicationBuilder

from src.bot.admin_handlers import register_admin_handlers, error_handler
from src.bot.handlers import register_handlers
from src.bot.scheduler import setup_scheduler
from src.config.config import app_settings
from src.config.logging_config import setup_logging
from src.services.summarizer import (
    pull_articles_and_save_articles,
    create_and_save_summaries,
)

logger = getLogger(__name__)

bot = Bot(token=app_settings.TELEGRAM_BOT_TOKEN)


def stage_1(as_of_date: dt.date):
    pull_articles_and_save_articles(as_of_date)


def stage_2(as_of_date: dt.date):
    create_and_save_summaries(as_of_date)


async def stage_3():
    await send_master_summaries()


async def main():
    """Main entry point for the bot."""
    bot_app = ApplicationBuilder().token(app_settings.TELEGRAM_BOT_TOKEN).build()

    # Register all handlers
    register_handlers(bot_app)
    register_admin_handlers(bot_app)

    setup_scheduler(bot_app)

    bot_app.add_error_handler(error_handler)

    try:
        print("Starting the bot...")
        await bot_app.start()
        await bot_app.idle()
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped.")
    finally:
        print("Shutting down the bot...")


if __name__ == "__main__":
    setup_logging()

    asyncio.run(main())

    parser = argparse.ArgumentParser()

    parser.add_argument("--as_of_date")

    parser.add_argument("--run_stage_1", action=argparse.BooleanOptionalAction)
    parser.add_argument("--run_stage_2", action=argparse.BooleanOptionalAction)
    parser.add_argument("--run_stage_3", action=argparse.BooleanOptionalAction)

    parser.add_argument("--test", action=argparse.BooleanOptionalAction)
    args = parser.parse_args()

    as_of_date = (
        dt.datetime.strptime(args.as_of_date, "%Y-%m-%d")
        if args.as_of_date
        else dt.datetime.today()
    )
    as_of_date = as_of_date.date()

    if args.run_stage_1:
        stage_1(as_of_date)
    if args.run_stage_2:
        stage_2(as_of_date)
    if args.run_stage_3:
        asyncio.run(stage_3())

    # scheduler = BackgroundScheduler()
    # scheduler.add_job(generate_daily_summaries, "cron", hour=18)
    # scheduler.start()

    # Schedule tasks
    # schedule.every().day.at("03:00").do(fetch_and_summarize_articles)  # 3 AM UTC
    # schedule.every().day.at("06:00").do(send_master_summaries)  # 6 AM UTC
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
