# News & YouTube Summarizer Bot

A dynamic Telegram bot that summarizes both cryptocurrency news and YouTube videos from selected channels. The bot delivers concise summaries to dedicated Telegram groups, making it easy to stay updated with the latest content.

## Features

### Crypto News Summaries
- Automatically summarizes cryptocurrency news articles
- Delivers daily updates to a dedicated Telegram group
- Integrates insights from on-chain data and technical analysis

### YouTube Channel Summaries
- Monitors selected YouTube channels for new videos
- Creates AI-powered summaries of video content
- Organizes summaries by channel in topic-based discussions
- Posts summaries with direct links to original videos

## Project Setup

### Prerequisites
- Python 3.8+
- PostgreSQL
- Telegram Bot Token
- YouTube API Key

### Environment Setup

1. Create `.env` file based on `.env.sample`

### Database Setup

1. Install PostgreSQL
2. Navigate to `sql` directory
3. Run `setup_database.bat`

The setup script will:
- Create database and required tables
- Set up indexes for better performance
- Configure necessary permissions

### Running the Application

In the project directory, run:
```bash
./run-all.cmd
```

## Telegram Bot Setup

1. Create a Telegram Supergroup
2. Enable Topics in group settings
3. Add the bot as administrator with permissions:
   - Send Messages
   - Edit Messages
   - Delete Messages
   - Pin Messages
   - Manage Topics
4. Use `/getchatid` command to get the group ID
5. Update `YOUTUBE_GROUP_CHAT_ID` in `.env`

## Bot Commands

- `/start` - Start interacting with the bot
- `/getchatid` - Get current chat ID
- `/info` - Get bot information
- `/join_the_channel` - Join Crypto Daily Brief channel

## Docker Support

To run using Docker:
```bash
docker build -t python-docker-image .
docker run python-docker-image
```

## Project Structure

```
text-summarization/
├── sql/                    # Database scripts
├── src/
│   ├── bot/               # Telegram bot handlers
│   ├── config/            # Configuration settings
│   ├── database/          # Database models
│   │   └── models/        
│   └── services/          # Core services
│       ├── youtube_client.py
│       └── youtube_summarizer.py
├── .env                   # Environment variables
└── requirements.txt       # Python dependencies
```

