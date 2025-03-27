-- Create tables if they don't exist

-- Create cryptonews_articles_dump table
CREATE TABLE IF NOT EXISTS cryptonews_articles_dump (
    id SERIAL PRIMARY KEY,
    news_url TEXT NOT NULL,
    image_url TEXT,
    title TEXT NOT NULL,
    text TEXT,
    source_name TEXT,
    date DATE,
    topics TEXT,
    sentiment TEXT,
    content_type TEXT,
    body TEXT,
    content_summary TEXT,
    master_summary TEXT,
    tags TEXT
);

-- Create youtube_channels table
CREATE TABLE IF NOT EXISTS youtube_channels (
    id SERIAL PRIMARY KEY,
    channel_id VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    topic_id INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    CONSTRAINT youtube_channels_channel_id_key UNIQUE (channel_id)
);

-- Create youtube_videos table
CREATE TABLE IF NOT EXISTS youtube_videos (
    id SERIAL PRIMARY KEY,
    video_id VARCHAR(255) NOT NULL,
    channel_id VARCHAR(255) NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    published_at TIMESTAMP WITH TIME ZONE NOT NULL,
    transcript TEXT,
    summary TEXT,
    processed_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT youtube_videos_video_id_key UNIQUE (video_id),
    CONSTRAINT fk_youtube_videos_channel
        FOREIGN KEY (channel_id)
        REFERENCES youtube_channels(channel_id)
        ON DELETE CASCADE
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_cryptonews_articles_date ON cryptonews_articles_dump(date);
CREATE INDEX IF NOT EXISTS idx_youtube_videos_published_at ON youtube_videos(published_at);
CREATE INDEX IF NOT EXISTS idx_youtube_videos_channel_id ON youtube_videos(channel_id);

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO postgres;
