import datetime as dt
import os
from logging import getLogger

from telegram import Update
from telegram.error import TelegramError
from telegram.ext import CallbackContext, CommandHandler, Application, ContextTypes

from src.bot.handlers import APP_START_TIME
from src.config.config import app_settings
from src.config.logging_config import LOG_DIR
from src.services.utils import get_today_logs, create_zip_archive, summarize_text

logger = getLogger(__name__)


def register_admin_handlers(app: Application) -> None:
    """Register admin commands."""

    app.add_handler(CommandHandler("health", health_check))
    app.add_handler(CommandHandler("send_logs", send_today_logs))
    app.add_handler(CommandHandler("send_all_logs", send_all_logs))
    app.add_handler(CommandHandler("story_summarize_link", send_story_summary))


async def health_check(update: Update, context: CallbackContext):
    """Handle the /health command."""
    uptime = dt.datetime.now() - APP_START_TIME
    health_message = (
        f"✅ Bot Status: Operational\n"
        f"⏱ Uptime: {uptime}\n"
        f"📂 Logs directory: {'Exists' if os.path.exists('logs') else 'Missing'}"
    )

    user_id = update.message.from_user.id
    if str(user_id) in app_settings.ADMIN_USER_IDS:
        await update.message.reply_text(health_message)
        logger.info(
            f"User {user_id} checked bot's status via /health command. Bot is live and running!"
        )
    else:
        logger.warning(
            f"You are not an admin user and not authorized "
            f"to perform /health command. User id: {user_id}."
        )


async def send_today_logs(update: Update, context: CallbackContext):
    """Handle the /send_logs command."""
    user_id = update.message.from_user.id

    if str(user_id) in app_settings.ADMIN_USER_IDS:
        today_logs = get_today_logs()

        if today_logs:
            zip_filename = create_zip_archive(today_logs)

            with open(zip_filename, "rb") as zip_file:
                await update.message.reply_document(
                    zip_file, caption="Here are today's logs."
                )

            os.remove(zip_filename)
            logger.info(f"Logs sent to user {user_id}.")
        else:
            logger.info("No logs found for today.")
            await update.message.reply_text("No logs found for today.")
    else:
        logger.warning(
            f"You are not an admin user and not authorized "
            f"to perform /send_logs command. User id: {user_id}."
        )


async def send_all_logs(update: Update, context: CallbackContext):
    """Handle the /send_all_logs command."""
    user_id = update.message.from_user.id

    if str(user_id) in app_settings.ADMIN_USER_IDS:
        all_logs = [
            os.path.join(LOG_DIR, f) for f in os.listdir(LOG_DIR) if f.endswith(".log")
        ]

        if all_logs:
            zip_filename = create_zip_archive(all_logs)

            with open(zip_filename, "rb") as zip_file:
                await update.message.reply_document(
                    zip_file, caption="Here are all the logs."
                )

            os.remove(zip_filename)
            logger.info(f"Logs sent to user {user_id}.")
        else:
            logger.info("No logs found for today.")
            await update.message.reply_text("No logs found.")
    else:
        logger.warning(
            f"You are not an admin user and not authorized "
            f"to perform /send_all_logs command. User id: {user_id}."
        )


async def send_story_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /story_summarize_link command."""
    user_id = update.message.from_user.id

    if str(user_id) in app_settings.ADMIN_USER_IDS:

        if context.args:
            news_url = " ".join(context.args)
            prompt = (
                "You are cryptocurrency expert. Summarize content of an article to create short, "
                "concise overview with required amount of details to inform users about daily changes in The Story community."
            )

            content_summary = summarize_text(news_url, prompt)

            await update.message.reply_text(content_summary)
        else:
            await update.message.reply_text("Please provide a link to summarize.")

    else:
        logger.warning(
            f"You are not an admin user and not authorized "
            f"to perform /health command. User id: {user_id}."
        )
