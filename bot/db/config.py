from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).parent


class Settings(BaseSettings):
    db_url: str = f"sqlite+aiosqlite:///bot/db/database.db"
    echo: bool = False


settings = Settings()

