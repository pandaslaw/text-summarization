from datetime import datetime, timedelta
import logging
from typing import List, Optional, Tuple

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import asyncio

from src.config.config import app_settings
from src.database.models.youtube import YouTubeChannel, YouTubeVideo

logger = logging.getLogger(__name__)


class YouTubeClient:
    def __init__(self):
        self.youtube = build("youtube", "v3", developerKey=app_settings.YOUTUBE_API_KEY)
        self.transcript_formatter = TextFormatter()

    async def _execute_youtube_api(self, request):
        """Execute YouTube API request asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, request.execute)

    async def get_channel_info(
        self, channel_url: str
    ) -> Optional[Tuple[str, str, str]]:
        """
        Get channel ID, name and description from channel URL.
        Returns tuple of (channel_id, name, description) or None if not found.
        """
        try:
            # Extract channel ID from URL
            if "youtube.com/channel/" in channel_url:
                channel_id = channel_url.split("youtube.com/channel/")[1].split("/")[0]
            elif "youtube.com/c/" in channel_url or "youtube.com/@" in channel_url:
                # For custom URLs, we need to search for the channel
                channel_name = channel_url.split("/")[-1].replace("@", "")
                search_response = await self._execute_youtube_api(
                    self.youtube.search().list(
                        q=channel_name, type="channel", part="id"
                    )
                )

                if not search_response["items"]:
                    return None

                channel_id = search_response["items"][0]["id"]["channelId"]
            else:
                logger.error(f"Invalid channel URL format: {channel_url}")
                return None

            # Get channel details
            channel_response = await self._execute_youtube_api(
                self.youtube.channels().list(part="snippet", id=channel_id)
            )

            if not channel_response["items"]:
                return None

            channel_info = channel_response["items"][0]["snippet"]
            return (
                channel_id,
                channel_info["title"],
                channel_info.get("description", ""),
            )

        except HttpError as e:
            logger.error(f"Error getting channel info: {e}")
            return None

    async def get_recent_videos(
        self, channel_id: str, after_date: datetime
    ) -> List[dict]:
        """Get videos published after specified date for a channel."""
        try:
            # Convert date to RFC 3339 format
            after_date_str = after_date.isoformat("T") + "Z"

            # Get videos
            search_response = await self._execute_youtube_api(
                self.youtube.search().list(
                    channelId=channel_id,
                    order="date",
                    type="video",
                    part="id,snippet",
                    publishedAfter=after_date_str,
                    maxResults=50,  # Adjust as needed
                )
            )

            videos = []
            for item in search_response.get("items", []):
                if item["id"]["kind"] == "youtube#video":
                    video_data = {
                        "video_id": item["id"]["videoId"],
                        "title": item["snippet"]["title"],
                        "description": item["snippet"]["description"],
                        "published_at": datetime.strptime(
                            item["snippet"]["publishedAt"], "%Y-%m-%dT%H:%M:%SZ"
                        ),
                    }
                    videos.append(video_data)

            return videos

        except HttpError as e:
            logger.error(f"Error getting videos for channel {channel_id}: {e}")
            return []

    async def get_video_transcript(self, video_id: str) -> Optional[str]:
        """Get transcript for a video."""
        try:
            loop = asyncio.get_event_loop()
            transcript_list = await loop.run_in_executor(
                None,
                lambda: YouTubeTranscriptApi.get_transcript(video_id, languages=["en"]),
            )

            # Format transcript to plain text
            return self.transcript_formatter.format_transcript(transcript_list)

        except Exception as e:
            logger.error(f"Error getting transcript for video {video_id}: {e}")
            return None

    async def process_channel_videos(
        self, channel: YouTubeChannel, session, get_recent_videos: bool = False
    ) -> List[YouTubeVideo]:
        """
        Process videos for a channel published in the last 24 hours.
        Returns list of processed videos.
        """
        after_date = datetime.utcnow() - timedelta(days=1)
        videos = await self.get_recent_videos(channel.channel_id, after_date)

        processed_videos = []
        for video_data in videos:
            # Check if video already exists
            existing_video = (
                session.query(YouTubeVideo)
                .filter_by(video_id=video_data["video_id"])
                .first()
            )

            if existing_video:
                if get_recent_videos:
                    processed_videos.append(existing_video)
                continue

            # Get transcript
            transcript = await self.get_video_transcript(video_data["video_id"])

            # Create new video
            video = YouTubeVideo(
                video_id=video_data["video_id"],
                channel_id=channel.channel_id,
                title=video_data["title"],
                description=video_data["description"],
                published_at=video_data["published_at"],
                transcript=transcript,
            )

            session.add(video)
            processed_videos.append(video)

        if processed_videos:
            session.commit()

        return processed_videos
