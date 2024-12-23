import asyncio
import datetime as dt
import sys
import traceback
from logging import getLogger

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CallbackContext, ContextTypes, CommandHandler, Application

from src.bot.utils import escape_markdown_v2, notify_admin_on_error, get_response_json, split_message
from src.config.config import app_settings
from src.config.constants import TICKERS, TOPICS
from src.database.connection import create_session
from src.database.database import get_master_summary
from src.run_bot import bot

logger = getLogger(__name__)

# Record bot's start time
APP_START_TIME = dt.datetime.now()


def register_handlers(app: Application):
    """Register all command and message handlers."""
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("create_topic", create_topic))
    app.add_handler(CommandHandler("get_topics", get_topics))
    app.add_handler(CommandHandler("validator_status", send_validator_status))
    # app.add_handler(CommandHandler("best_validator", get_best_validator))


async def start(update: Update, context: CallbackContext):
    """Handle the /start command."""
    await update.message.reply_text(
        "Welcome to the News Summary Bot! Use /subscribe to subscribe to a channel."
    )


async def create_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /create_topic command."""
    # Check if user provided a topic name
    if context.args:
        topic_name = " ".join(context.args)

        # Create the topic in the chat
        chat = update.effective_chat

        try:
            # Create the forum topic (requires bot to be an admin with can_manage_topics permission)
            result = await chat.create_forum_topic(name=topic_name)
            await update.message.reply_text(
                f"Topic '{topic_name}' created successfully!"
            )
        except Exception as e:
            await update.message.reply_text(f"Failed to create topic: {str(e)}")
    else:
        await update.message.reply_text("Please provide a topic name.")


async def get_topics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetch and display current topics."""
    user = update.effective_user
    chat = update.effective_chat
    thread_id = update.message.message_thread_id

    is_admin = user.id in [
        admin.user.id for admin in await context.bot.get_chat_administrators(chat.id)
    ]
    if not is_admin:
        await context.bot.send_message(
            chat_id=chat.id,
            text="Only admins use this command.",
            message_thread_id=thread_id,
        )
        return

    # check if the message is a reply to another message
    if not update.message.reply_to_message:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Please reply to a player to award a point.",
            message_thread_id=thread_id,
        )
        return


async def send_master_summaries(as_of_date, bot_app):
    """Generate and send master summaries for each topic."""

    with create_session() as session:
        try:
            for ticker in TICKERS:
                logger.info(f"Loading master summary for '{ticker}' ticker...")
                master_summary = get_master_summary(session, as_of_date, ticker)

                if not master_summary:
                    logger.warning(f"Master summary is missing for '{ticker}' ticker for on {as_of_date}. SKIPPING.")
                    continue

                escaped_summary = escape_markdown_v2(master_summary)

                message = await bot.send_message(
                    chat_id=app_settings.GROUP_CHAT_ID,
                    text=escaped_summary,
                    parse_mode=ParseMode.MARKDOWN_V2,
                    message_thread_id=TOPICS[ticker],
                )
                logger.info(f"Sent master summary to '{ticker}' topic, message ID: {message.message_id}.")
                await asyncio.sleep(1)

            logger.info(f"Successfully finished with sending master summaries to {len(TICKERS)} topics.")
        except Exception as e:
            error_message = f"Error sending master summary to '{ticker}' topic: {e}"
            logger.error(error_message)
            await notify_admin_on_error(bot_app.bot, error_message)


def get_validator_info(items, active_only: bool, compact_format=True):
    status_mapping = {1: "Jail", 2: "Inactive", 3: "Active"}

    try:
        # User data with defaults
        name = items.get("description", {}).get("moniker", "Unknown Validator")
        operator_address = items.get("operator_address", "Unknown Address")

        # Metadata with defaults
        status_int = items.get("status", 0)
        status = status_mapping.get(status_int, "Unknown Status")
        windowUptime = items.get("uptime", {}).get("windowUptime", {})
        uptime = round(windowUptime.get("uptime", 0) * 100, 2) if windowUptime else 0
        commission_str = items.get("commission", {}).get("commission_rates", {}).get("rate", "0")
        commission = round(float(commission_str) * 100, 2)


    except Exception as e:
        logger.error(f"Failed to extract metadata from json: {e}")
        logger.error(items)
        raise Exception(e)

    link_to_page = rf"https://testnet.storyscan.app/validators/{operator_address}?tab=profile"

    if compact_format:
        status_message = (
            f"<a href='{link_to_page}'>{name}</a> ✅ Status: {status} ⏱ Uptime: {uptime}% 💸 Commission: {commission}%\n"
        )
    else:
        status_message = (
            f"<a href='{link_to_page}'>{name}</a>\n"
            f"✅ Status: {status}\n"
            f"⏱ Uptime: {uptime}%\n"
            f"💸 Commission: {commission}%\n"
        )

    if active_only and status_int != 3:
        return ""
    return status_message


async def send_validator_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /validator_status command."""
    if context.args:
        validator_user_name = " ".join(context.args)
        url = f"https://api.testnet.storyscan.app/validators?name={validator_user_name}"

        response_json = get_response_json(url)
        items = response_json["items"][0]
        validator_info = get_validator_info(items, active_only=False, compact_format=False)

        await update.message.reply_text(validator_info, parse_mode='HTML', disable_web_page_preview=True)
    else:
        url = "https://api.testnet.storyscan.app/validators/active"

        try:
            await update.message.reply_text("Requesting info for all active validators...")

            all_items = get_response_json(f"{url}")
            logger.info(f"Got {len(all_items)} validator jsons. Starting to extract metainfo...")

            status_messages = []
            for item in all_items:
                status_message = get_validator_info(item, active_only=True, compact_format=True)
                if status_message:
                    status_messages.append(status_message)

            status_messages_str = "\n".join(status_messages)

            logger.info(f"Split the message into chunks.")
            message_chunks = split_message(status_messages_str)

            # Send each chunk
            for chunk in message_chunks:
                await update.message.reply_text(chunk, parse_mode='HTML', disable_web_page_preview=True)
                await asyncio.sleep(1)
            logger.info(f"Succesfully sent validator metainfo.")
        except Exception as e:
            exc_type, exc_value, exc_tb = sys.exc_info()
            tb_summary = traceback.extract_tb(exc_tb)

            error_message = f"Error pulling info about validators: {e}"
            messages = [error_message]
            logger.error(error_message)

            for tb in tb_summary:
                message = f"File: {tb.filename}, Line: {tb.lineno}, Function: {tb.name}, Code: {tb.line}"
                messages.append(message)
                logger.error(message)

            await update.message.reply_text(error_message)


async def get_best_validator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /best_validator command."""
    url = f"https://api.testnet.storyscan.app/validators"

    response_json = get_response_json(url)
    items = response_json["items"][0]
    status = items["status"]
    commission_str = items["commission"]["commission_rates"]["rate"]
    commission = float(commission_str) * 100

    uptime = items["uptime"]["windowUptime"]["uptime"] * 100

    health_message = (
        f"⏱ Uptime: {uptime}%\n"
        f"⏱ Commission: {commission}\n"
    )

    await update.message.reply_text(health_message)
