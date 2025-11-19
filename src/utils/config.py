"""Configuration module for the application"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    APP_NAME: str = "JetRecon"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "High-performance Data Reconciliation Tool"

    DEFAULT_HOST: str = "0.0.0.0"
    DEFAULT_PORT: str = "8000"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


config = Config()
