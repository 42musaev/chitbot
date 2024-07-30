from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    BOT_TOKEN: str
    DEBUG: bool = True
    KICK_TIMEOUT: int = 30
    CHATS: dict
    TOPICS: dict
    DATABASE_URL: str


settings = Settings()
