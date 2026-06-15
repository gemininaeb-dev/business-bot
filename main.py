"""Точка входа: одновременно запускает Telegram-бота и веб-панель.

Бот работает на long-polling, веб-панель — на uvicorn. Оба компонента
живут в одном asyncio-цикле и используют общую базу данных.
"""

from __future__ import annotations

import asyncio
import logging

import uvicorn

from app.bot.bot import create_bot, create_dispatcher
from app.config import get_settings
from app.db.session import init_db
from app.web.app import app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("business-bot")


async def _run_bot() -> None:
    """Запускает long-polling Telegram-бота."""
    bot = create_bot()
    dp = create_dispatcher()
    logger.info("Бот запущен (polling)")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


async def _run_web() -> None:
    """Запускает веб-панель на uvicorn."""
    settings = get_settings()
    config = uvicorn.Config(
        app,
        host=settings.web_host,
        port=settings.web_port,
        log_level="info",
    )
    server = uvicorn.Server(config)
    logger.info("Веб-панель запущена на http://%s:%s", settings.web_host, settings.web_port)
    await server.serve()


async def main() -> None:
    """Инициализирует БД и поднимает бота и веб параллельно."""
    await init_db()
    await asyncio.gather(_run_bot(), _run_web())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Остановлено")
