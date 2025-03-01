import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session
from telegram.ext import Application

from src.config.config import app_settings
from src.database.models.youtube import YouTubeChannel, YouTubeVideo
from src.services.utils import summarize_text
from src.services.youtube_client import YouTubeClient

logger = logging.getLogger(__name__)

class YouTubeSummarizer:
    def __init__(self, session: Session, bot_app: Application):
        self.session = session
        self.bot_app = bot_app
        self.youtube_client = YouTubeClient()

    async def add_channel(self, channel_url: str) -> Optional[YouTubeChannel]:
        """Add a new YouTube channel to monitor."""
        channel_info = await self.youtube_client.get_channel_info(channel_url)
        if not channel_info:
            return None

        channel_id, name, description = channel_info
        
        # Check if channel already exists
        existing_channel = self.session.query(YouTubeChannel).filter_by(
            channel_id=channel_id
        ).first()
        
        if existing_channel:
            return existing_channel

        # Create new channel
        channel = YouTubeChannel(
            channel_id=channel_id,
            name=name,
            description=description
        )
        
        self.session.add(channel)
        self.session.commit()
        
        return channel

    def process_video(self, video: YouTubeVideo) -> bool:
        """
        Process a single video: generate summary if transcript is available.
        Returns True if summary was generated successfully.
        """
        if not video.transcript:
            logger.warning(f"No transcript available for video {video.video_id}")
            return False

        try:
            # Generate summary using existing summarization infrastructure
            summary = summarize_text(
                video.transcript,
                app_settings.YOUTUBE_SUMMARY_PROMPT
            )
            
            video.summary = summary
            video.processed_at = datetime.utcnow()
            self.session.commit()
            
            return True

        except Exception as e:
            logger.error(f"Error processing video {video.video_id}: {e}")
            return False

    async def send_summary_to_telegram(self, video: YouTubeVideo):
        """Send video summary to Telegram channel."""
        if not video.summary:
            return

        channel = video.channel
        message = (
            f"🎥 *New Video from {channel.name}*\n\n"
            f"*{video.title}*\n\n"
            f"{video.summary}\n\n"
            f"🔗 [Watch on YouTube](https://www.youtube.com/watch?v={video.video_id})"
        )

        try:
            await self.bot_app.bot.send_message(
                chat_id=app_settings.YOUTUBE_GROUP_CHAT_ID,
                text=message,
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
        except Exception as e:
            logger.error(f"Error sending summary to Telegram: {e}")

    async def process_all_channels(self):
        """Process all active channels and generate summaries for new videos."""
        active_channels = self.session.query(YouTubeChannel).filter_by(
            is_active=True
        ).all()

        for channel in active_channels:
            try:
                # Get and process new videos
                new_videos = await self.youtube_client.process_channel_videos(channel, self.session)
                
                for video in new_videos:
                    if self.process_video(video):
                        await self.send_summary_to_telegram(video)
                    
            except Exception as e:
                logger.error(f"Error processing channel {channel.name}: {e}")
                continue
