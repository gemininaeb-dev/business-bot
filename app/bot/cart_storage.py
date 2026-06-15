"""Простое хранилище корзин в памяти (по Telegram ID клиента).

Для портфолио/демо этого достаточно. В продакшене корзину можно
перенести в Redis — интерфейс останется тем же.
"""

from __future__ import annotations

from app.services.cart import Cart

_carts: dict[int, Cart] = {}


def get_cart(telegram_id: int) -> Cart:
    """Возвращает корзину клиента, создавая пустую при необходимости."""
    return _carts.setdefault(telegram_id, Cart())


def clear_cart(telegram_id: int) -> None:
    """Удаляет корзину клиента."""
    _carts.pop(telegram_id, None)
