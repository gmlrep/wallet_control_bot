import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).parent

load_dotenv()


class Settings(BaseSettings):
    bot_token: str = os.getenv('BOT_TOKEN')

    api_token: str = os.getenv('API_KEY')

    db_url: str = f"sqlite+aiosqlite:///{BASE_DIR}/database.db"
    echo: bool = False

    time_scheduler: str = os.getenv('TIME')


settings = Settings()
