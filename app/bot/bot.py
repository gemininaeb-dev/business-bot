"""Создание и настройка бота и диспетчера aiogram."""

from __future__ import annotations

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.bot.handlers import cart, catalog, orders, start
from app.bot.middlewares import DbSessionMiddleware
from app.config import get_settings


def create_bot() -> Bot:
    """Создаёт экземпляр бота с HTML-разметкой по умолчанию."""
    return Bot(
        token=get_settings().bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def create_dispatcher() -> Dispatcher:
    """Собирает диспетчер: middleware + все роутеры."""
    dp = Dispatcher()

    session_mw = DbSessionMiddleware()
    dp.message.middleware(session_mw)
    dp.callback_query.middleware(session_mw)

    dp.include_router(start.router)
    dp.include_router(catalog.router)
    dp.include_router(cart.router)
    dp.include_router(orders.router)
    return dp
