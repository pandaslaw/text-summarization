import os
from logging import getLogger
from typing import List

import yaml
from dotenv import load_dotenv
from pydantic.v1 import BaseSettings

logger = getLogger(__name__)


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
    TELEGRAM_BOT_TOKEN: str
    GROUP_CHAT_ID: int

    DISCORD_BOT_TOKEN: str
    DISCORD_CHANNEL_ID: int

    # Prompts loaded from YAML
    CONTENT_SUMMARY_PROMPT: str = None
    MASTER_SUMMARY_PROMPT: str = None

    def load_prompts_from_yaml(self, yaml_file="prompts.yaml"):
        """Load prompts from the specified YAML file."""
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
        docs_dir = "data"
        yaml_file_full_path = os.path.join(root_dir, docs_dir, yaml_file)

        with open(yaml_file_full_path, "r", encoding="utf-8") as file:
            prompts = yaml.safe_load(file)

        self.CONTENT_SUMMARY_PROMPT = prompts.get("content_summary_prompt", "")
        self.MASTER_SUMMARY_PROMPT = prompts.get("master_summary_prompt", "")


logger.info("Loading environment variables from .env file.")
load_dotenv()
app_settings = AppSettings()
app_settings.load_prompts_from_yaml()
app_settings.HUGGINGFACE_HEADERS = {
    "Authorization": f"Bearer {app_settings.HUGGINGFACE_API_KEY}"
}

logger.info(f"CONFIG (DEBUG_MODE): {app_settings.DEBUG_MODE}")
logger.info(f"CONFIG (LANGUAGE_MODEL): {app_settings.LANGUAGE_MODEL}")
logger.info(f"CONFIG (GROUP_CHAT_ID): {app_settings.GROUP_CHAT_ID}")
logger.info(f"CONFIG (ADMIN_USER_IDS): {app_settings.ADMIN_USER_IDS}")
logger.info(f"CONFIG (CONTENT_SUMMARY_PROMPT): {app_settings.CONTENT_SUMMARY_PROMPT}")
logger.info(f"CONFIG (MASTER_SUMMARY_PROMPT): {app_settings.MASTER_SUMMARY_PROMPT}")
logger.info("-------------ENV VARIABLES INITIALIZATION FINISHED-------------\n\n")
