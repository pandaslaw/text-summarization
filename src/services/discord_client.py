from logging import getLogger
from typing import Any

import discord
from discord import Intents

from src.config.config import app_settings
import datetime as dt

from src.services.utils import summarize_text

logger = getLogger(__name__)


class DiscordClient(discord.Client):

    def __init__(self, bot_app, *, intents: Intents, **options: Any):
        super().__init__(intents=intents, **options)
        self.bot_app = bot_app

    async def on_ready(self):
        print(f"Logged in as {self.user}")
        await self.fetch_and_summarize()

    async def fetch_and_summarize(self):
        channel = self.get_channel(app_settings.DISCORD_CHANNEL_ID)
        if not channel:
            print("Channel not found!")
            return

        # Fetch messages from the last 24 hours
        today = dt.datetime.utcnow()
        yesterday = today - dt.timedelta(days=1)
        messages = await channel.history(after=yesterday, limit=100).flatten()

        # Concatenate all messages into a single string for summarization
        content = "\n".join(
            [message.content for message in messages if message.content]
        )
        if not content:
            print("No messages found to summarize.")
            return

        # Summarize using OpenAI GPT
        prompt = "Summarize discords channel messages to have comprehensive"
        summary = summarize_text(content, prompt)

        # Send summary to Telegram
        await self.send_summary_to_telegram(summary)

    async def send_summary_to_telegram(self, summary):
        try:
            async with self.bot_app as bot_app:
                await bot_app.bot.send_message(chat_id=app_settings.Te, text=summary)
            logger.info("Summary sent to Telegram!")
        except Exception as e:
            print(f"Error sending summary to Telegram: {e}")


async def run_scheduled_task(bot_app):
    """Run the scheduled task to summarize and send news."""
    intents = discord.Intents.default()
    intents.messages = True
    intents.message_content = True

    discord_client = DiscordClient(bot_app, intents=intents)

    # Start the Discord client
    await discord_client.start(app_settings.DISCORD_BOT_TOKEN)

    # After the client is running, you can fetch and summarize
    await discord_client.fetch_and_summarize()
