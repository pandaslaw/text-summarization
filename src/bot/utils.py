from logging import getLogger

import requests
from telegram.error import TelegramError
from telegram.ext import CallbackContext

from src.config.config import app_settings

logger = getLogger(__name__)


def get_response_json(url: str):
    response = requests.get(url)

    if response is not None and response.status_code != 200:
        logger.error(f"Error on requesting 'url': {response.content}")
        raise Exception(response.content)

    response_json = response.json()
    return response_json


def escape_markdown_v2(text):
    """Escape special characters for MarkdownV2."""
    return (
        text.replace("_", "\\_")
        .replace("*", "\\*")
        .replace("[", "\\[")
        .replace("]", "\\]")
        .replace("(", "\\(")
        .replace(")", "\\)")
        .replace("~", "\\~")
        .replace("`", "\\`")
        .replace(">", "\\>")
        .replace("#", "\\#")
        .replace("+", "\\+")
        .replace("-", "\\-")
        .replace("=", "\\=")
        .replace("|", "\\|")
        .replace("{", "\\{")
        .replace("}", "\\}")
        .replace(".", "\\.")
        .replace("!", "\\!")
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
            logger.info(
                f"Trying to send a notification to admin user with id={admin_chat_id}"
            )
            await bot_app.send_message(
                chat_id=admin_chat_id, text=f"Error occurred: {error_message}"
            )
    except Exception as e:
        logger.error(f"Failed to notify admin: {e}")


def split_message(message: str, max_length: int = 4096) -> list:
    """Split the message into chunks of max_length."""
    chunks = []
    current_chunk = ""

    for line in message.split("\n"):
        # Check the length if we add this line
        if len(current_chunk) + len(line) + 1 > max_length:  # +1 for the newline
            if current_chunk:  # If current chunk is not empty, add it to chunks
                chunks.append(current_chunk)
            current_chunk = line  # Start a new chunk with the current line
        else:
            if current_chunk:  # If current chunk is not empty, add a newline first
                current_chunk += "\n"
            current_chunk += line

    # Add any remaining chunk
    if current_chunk:
        chunks.append(current_chunk)

    return chunks
