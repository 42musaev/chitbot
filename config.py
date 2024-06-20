from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    BOT_TOKEN: str
    DEBUG: bool = True


settings = Settings()
