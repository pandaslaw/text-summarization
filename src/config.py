from typing import List

from dotenv import load_dotenv
from loguru import logger
from pydantic.v1 import BaseSettings


class AppSettings(BaseSettings):
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    DEBUG_MODE: bool

    DB_CONNECTION_STRING: str

    CRYPTONEWS_API_KEY: str

    OPENAI_API_KEY: str
    OPENROUTER_API_KEY: str
    HUGGINGFACE_API_KEY: str
    HUGGINGFACE_HEADERS: dict = None

    LANGUAGE_MODEL: str

    ADMIN_USER_IDS: List[str] = []

    PROMPT_FOR_CONTENT_SUMMARY: str
    PROMPT_FOR_MASTER_SUMMARY: str


logger.info("Loading environment variables from .env file.")
load_dotenv()
app_settings = AppSettings()
app_settings.HUGGINGFACE_HEADERS = {
    "Authorization": f"Bearer {app_settings.HUGGINGFACE_API_KEY}"
}


logger.info(f"CONFIG (DEBUG_MODE): {app_settings.DEBUG_MODE}")
logger.info(f"CONFIG (LANGUAGE_MODEL): {app_settings.LANGUAGE_MODEL}")
logger.info(f"CONFIG (BOT_USER_ID): {app_settings.BOT_USER_ID}")
logger.info(f"CONFIG (ADMIN_USER_IDS): {app_settings.ADMIN_USER_IDS}")
logger.info(
    f"CONFIG (PROMPT_FOR_CONTENT_SUMMARY): {app_settings.PROMPT_FOR_CONTENT_SUMMARY}"
)
logger.info(
    f"CONFIG (PROMPT_FOR_MASTER_SUMMARY): {app_settings.PROMPT_FOR_MASTER_SUMMARY}"
)
logger.info("-------------ENV VARIABLES INITIALIZATION FINISHED-------------\n\n")
