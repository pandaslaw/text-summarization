import asyncio
from logging import getLogger

from telegram.ext import ApplicationBuilder

from src.bot.admin_handlers import register_admin_handlers, error_handler
from src.bot.handlers import register_handlers
from src.bot.scheduler import setup_scheduler
from src.config.config import app_settings
from src.config.logging_config import setup_logging

logger = getLogger(__name__)


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
