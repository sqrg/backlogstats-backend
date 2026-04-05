from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DATABASE_URL: str
    DEBUG: bool = False
    APP_ENV: Literal["local", "staging", "production"] = "local"

    IGDB_CLIENT_ID: str = ""
    IGDB_CLIENT_SECRET: str = ""

    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    DISCORD_CLIENT_ID: str = ""
    DISCORD_CLIENT_SECRET: str = ""


settings = Settings()
