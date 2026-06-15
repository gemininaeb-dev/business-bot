"""Конфигурация приложения, читается из переменных окружения (.env)."""

from functools import lru_cache

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Все настройки проекта в одном месте."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Telegram
    bot_token: str
    admin_ids: list[int] = []

    # База данных
    database_url: str = "sqlite+aiosqlite:///./business_bot.db"

    # Веб-панель
    admin_login: str = "admin"
    admin_password: str = "admin"
    secret_key: str = "dev-secret-change-me"
    web_host: str = "0.0.0.0"
    # Хостинги (Railway/Render) передают порт через переменную PORT
    web_port: int = Field(
        default=8000,
        validation_alias=AliasChoices("WEB_PORT", "PORT"),
    )

    # Брендинг
    business_name: str = "Мой бизнес"

    @field_validator("admin_ids", mode="before")
    @classmethod
    def _parse_admin_ids(cls, value: object) -> list[int]:
        """Позволяет задавать ADMIN_IDS как '123,456' в .env."""
        if isinstance(value, str):
            return [int(x) for x in value.split(",") if x.strip()]
        if isinstance(value, list):
            return [int(x) for x in value]
        return []


@lru_cache
def get_settings() -> Settings:
    """Возвращает единственный экземпляр настроек (кэшируется)."""
    return Settings()
