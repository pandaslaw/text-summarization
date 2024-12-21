from telegram import Update, ForumTopic
from telegram.constants import ParseMode

from src.bot.utils import escape_markdown_v2
from src.config import app_settings
from src.constants import TICKERS, TOPICS
from src.database import create_session, get_master_summary
import datetime as dt

from src.run_bot import bot
from src.summarization.utils.utils import logger


async def send_master_summaries():
    """Generate and send master summaries for each topic."""
    as_of_date = dt.datetime.utcnow().date()

    with create_session() as session:
        for ticker in TICKERS:
            try:
                master_summary = get_master_summary(session, as_of_date, ticker)

                escaped_summary = escape_markdown_v2(master_summary)

                await bot.send_message(
                    chat_id=app_settings.GROUP_CHAT_ID,
                    text=escaped_summary,
                    parse_mode=ParseMode.MARKDOWN_V2,
                    message_thread_id=TOPICS[ticker],
                )
                logger.info(f"Sent master summary to '{ticker}' topic.")
            except Exception as e:
                print(f"Error sending master summary to '{ticker}' topic: {e}")
