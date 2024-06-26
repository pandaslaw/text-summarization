from dotenv import load_dotenv
from loguru import logger
from pydantic.v1 import BaseSettings


class AppSettings(BaseSettings):
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    OPENAI_API_KEY: str
    HUGGINGFACE_API_KEY: str
    HUGGINGFACE_HEADERS: dict = None
    CRYPTONEWS_API_KEY: str
    DATABASE_URL: str
    PROMPT_FOR_CONTENT_SUMMARY: str
    PROMPT_FOR_MASTER_SUMMARY: str


logger.info("Loading environment variables from .env file.")
load_dotenv()
app_settings = AppSettings()
app_settings.HUGGINGFACE_HEADERS = {"Authorization": f"Bearer {app_settings.HUGGINGFACE_API_KEY}"}
