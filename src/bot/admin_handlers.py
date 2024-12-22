import datetime as dt
import os
from logging import getLogger

from telegram import Update
from telegram.error import TelegramError
from telegram.ext import CallbackContext, CommandHandler, Application

from src.bot.handlers import APP_START_TIME
from src.config.config import app_settings
from src.config.logging_config import LOG_DIR
from src.services.utils import get_today_logs, create_zip_archive

logger = getLogger(__name__)


def register_admin_handlers(app: Application) -> None:
    """Register admin commands."""

    app.add_handler(CommandHandler("health", health_check))
    app.add_handler(CommandHandler("send_logs", send_today_logs))
    app.add_handler(CommandHandler("send_all_logs", send_all_logs))


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


async def error_handler(update: object, context: CallbackContext):
    """Log the error and notify admins."""
    error_message = f"An error occurred: {context.error}"
    logger.error(error_message)

    try:
        for admin_chat_id in app_settings.ADMIN_USER_IDS:
            await context.bot.send_message(chat_id=admin_chat_id, text=error_message)
    except TelegramError as notify_error:
        logger.error(f"Failed to notify admin: {notify_error}")


async def notify_admin_on_error(bot_app, error_message):
    """Send error notification to the admin."""
    try:
        for admin_chat_id in app_settings.ADMIN_USER_IDS:
            await bot_app.bot.send_message(
                chat_id=admin_chat_id, text=f"Error occurred: {error_message}"
            )
    except Exception as e:
        logger.error(f"Failed to notify admin: {e}")


# await notify_admin_on_error(bot_app, str(e))
