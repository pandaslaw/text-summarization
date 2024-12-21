from telegram import Bot
from telegram.ext import CommandHandler, ApplicationBuilder

from src.bot.handlers.start_handler import start, create_topic, get_topics
from src.config import app_settings


# Initialize clients
bot = Bot(token=app_settings.TELEGRAM_BOT_TOKEN)
app = ApplicationBuilder().token(app_settings.TELEGRAM_BOT_TOKEN).build()


if __name__ == "__main__":
    # Register commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("create_topic", create_topic))
    app.add_handler(CommandHandler("get_topics", get_topics))

    app.run_polling()
