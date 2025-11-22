"""Configuration module for the application"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    APP_NAME: str = "JetRecon"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "High-performance Data Reconciliation Tool"

    DEFAULT_HOST: str = "0.0.0.0"
    DEFAULT_PORT: int = 8000

    CHUNK_SIZE: int = 5
    MEMORY_USAGE_FACTOR: float = 0.625
    MEMORY_SAFETY_BUFFER: float = 0.90
    WOKER_MULTIPLIER: int = 2
    CPU_CORES_RESERVE: int = 2

    MIN_BUCKETS: int = 8
    MAX_BUCKETS: int = 5000
    MIN_BUCKET_SIZE: int = 5
    MAX_BUCKET_SIZE: int = 100

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


config = Config()
