import logging
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/phonebook"
    HOST_URL: str = "http://localhost:8000/phonebook/contacts"

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    CACHE_TTL: int = 3600

    METRICS_PREFIX: str = "phonebook"

    LOG_LEVEL: str = "DEBUG"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    PAGINATION_DEFAULT_PAGE: int = 10
    PAGINATION_MAX_PAGE: int = 100

    DEBUG: bool = False


settings = Settings()


class Messages:
    NUM_CONTACTS = "num_contacts"


class Logs:
    LOG_LEVELS = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    LOG_FORMAT = settings.LOG_FORMAT
