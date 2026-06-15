"""Заявки клиента и обработка действий администратора."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.models import OrderStatus
from app.db.repositories import OrderRepository, UserRepository
from app.services.orders import OrderService

router = Router()

_STATUS_LABELS = {
    OrderStatus.NEW: "🆕 Новая",
    OrderStatus.IN_PROGRESS: "🔧 В работе",
    OrderStatus.DONE: "✅ Готово",
    OrderStatus.CANCELLED: "❌ Отменена",
}


@router.message(F.text == "📋 Мои заявки")
async def my_orders(message: Message, session: AsyncSession) -> None:
    """Показывает последние заявки клиента."""
    assert message.from_user is not None
    users = UserRepository(session)
    user = await users.get_by_telegram_id(message.from_user.id)
    if user is None:
        await message.answer("Сначала зарегистрируйтесь через /start")
        return

    orders_repo = OrderRepository(session)
    all_orders = await orders_repo.list_filtered()
    mine = [o for o in all_orders if o.user_id == user.id][:10]
    if not mine:
        await message.answer("У вас пока нет заявок.")
        return

    lines = ["<b>Ваши заявки:</b>", ""]
    for order in mine:
        label = _STATUS_LABELS.get(order.status, order.status.value)
        lines.append(f"№{order.id} — {order.total:.0f} ₽ — {label}")
    await message.answer("\n".join(lines))


@router.callback_query(F.data.startswith("adm_status:"))
async def admin_change_status(callback: CallbackQuery, session: AsyncSession) -> None:
    """Админ меняет статус заявки прямо из уведомления."""
    if callback.from_user.id not in get_settings().admin_ids:
        await callback.answer("Недостаточно прав", show_alert=True)
        return

    assert callback.data is not None
    _, order_id_str, status_str = callback.data.split(":")
    status = OrderStatus(status_str)

    orders = OrderService(session)
    order = await orders.change_status(int(order_id_str), status)
    if order is None:
        await callback.answer("Заявка не найдена", show_alert=True)
        return

    await callback.answer(f"Статус: {_STATUS_LABELS[status]}")
    message = callback.message
    if isinstance(message, Message) and message.text:
        await message.edit_text(f"{message.text}\n\n➡️ Статус: {_STATUS_LABELS[status]}")
