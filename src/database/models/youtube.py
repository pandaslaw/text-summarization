from datetime import datetime
from sqlalchemy import Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import mapped_column, relationship
from src.database.models.summary import Base


class YouTubeChannel(Base):
    __tablename__ = "youtube_channels"

    id = mapped_column(Integer, primary_key=True)
    channel_id = mapped_column(String, nullable=False, unique=True)
    name = mapped_column(String, nullable=False)
    description = mapped_column(String, nullable=True)
    topic_id = mapped_column(Integer, nullable=True)  # Store Telegram topic ID
    created_at = mapped_column(DateTime, default=datetime.utcnow)
    is_active = mapped_column(Boolean, default=True)

    # Relationship to videos
    videos = relationship("YouTubeVideo", back_populates="channel")


class YouTubeVideo(Base):
    __tablename__ = "youtube_videos"

    id = mapped_column(Integer, primary_key=True)
    video_id = mapped_column(String, nullable=False, unique=True)
    channel_id = mapped_column(String, ForeignKey("youtube_channels.channel_id"))
    title = mapped_column(String, nullable=False)
    description = mapped_column(String, nullable=True)
    published_at = mapped_column(DateTime, nullable=False)
    transcript = mapped_column(String, nullable=True)
    summary = mapped_column(String, nullable=True)
    processed_at = mapped_column(DateTime, nullable=True)

    # Relationship to channel
    channel = relationship("YouTubeChannel", back_populates="videos")
