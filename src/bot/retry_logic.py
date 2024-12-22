import asyncio
from logging import getLogger

logger = getLogger(__name__)


async def retry(func, retries=3, delay=2, *args, **kwargs):
    """Retry a function if it fails."""
    for attempt in range(retries):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {e}")
            await asyncio.sleep(delay)
    raise Exception("All retry attempts failed.")


# await retry(bot_app.bot.send_message, retries=3, delay=5, chat_id=chat_id, text="Hello!")
