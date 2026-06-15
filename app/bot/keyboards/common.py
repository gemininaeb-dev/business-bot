"""Клавиатуры бота."""

from __future__ import annotations

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.db.models import Product


def main_menu() -> ReplyKeyboardMarkup:
    """Главное меню (нижняя клавиатура)."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛍 Каталог"), KeyboardButton(text="🛒 Корзина")],
            [KeyboardButton(text="📋 Мои заявки"), KeyboardButton(text="📞 Контакты")],
        ],
        resize_keyboard=True,
    )


def request_phone() -> ReplyKeyboardMarkup:
    """Запрос номера телефона при регистрации."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Отправить номер", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def product_card(product: Product) -> InlineKeyboardMarkup:
    """Кнопки под карточкой товара."""
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ В корзину", callback_data=f"add:{product.id}")
    return builder.as_markup()


def cart_actions() -> InlineKeyboardMarkup:
    """Кнопки управления корзиной."""
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Оформить заявку", callback_data="checkout")
    builder.button(text="🗑 Очистить", callback_data="clear_cart")
    builder.adjust(1)
    return builder.as_markup()


def confirm_order() -> InlineKeyboardMarkup:
    """Подтверждение оформления заявки."""
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить", callback_data="confirm")
    builder.button(text="❌ Отмена", callback_data="cancel")
    builder.adjust(2)
    return builder.as_markup()


def admin_order_actions(order_id: int) -> InlineKeyboardMarkup:
    """Кнопки для админа в уведомлении о новой заявке."""
    builder = InlineKeyboardBuilder()
    builder.button(text="🔧 В работу", callback_data=f"adm_status:{order_id}:in_progress")
    builder.button(text="✅ Готово", callback_data=f"adm_status:{order_id}:done")
    builder.adjust(2)
    return builder.as_markup()


def back_button(callback: str = "back_to_menu") -> InlineKeyboardButton:
    """Универсальная кнопка «Назад»."""
    return InlineKeyboardButton(text="⬅️ Назад", callback_data=callback)
