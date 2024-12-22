from logging import getLogger

from telegram import Bot
from telegram.ext import CommandHandler, ApplicationBuilder

from src.bot import handlers
from src.config.config import app_settings

logger = getLogger(__name__)

# Initialize clients
#   1. Bot: It is suitable for simple actions without needing to set up an event-driven system and for manual API calls
bot = Bot(token=app_settings.TELEGRAM_BOT_TOKEN)
#   2. ApplicationBuilder: Real-time interaction with users (e.g., responding to commands like /start or /help) with multiple handlers and event-driven workflows..
app = ApplicationBuilder().token(app_settings.TELEGRAM_BOT_TOKEN).build()

if __name__ == "__main__":
    # Register commands
    app.add_handler(CommandHandler("start", handlers.start))
    app.add_handler(CommandHandler("create_topic", handlers.create_topic))
    app.add_handler(CommandHandler("get_topics", handlers.get_topics))

    app.run_polling()
