"""Centralized configuration loaded from environment variables (.env)."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://scheduler:scheduler@localhost:5432/scheduler"
    heartbeat_interval_seconds: int = 5
    # worker considered OFFLINE after this many seconds without a heartbeat
    heartbeat_timeout_seconds: int = 15
    # how often the recovery loop scans for offline workers
    recovery_check_interval_seconds: int = 5
    log_level: str = "INFO"
    cors_origins: str = "*"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
