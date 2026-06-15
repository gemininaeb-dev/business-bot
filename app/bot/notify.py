"""Уведомления администраторам о событиях бота."""

from __future__ import annotations

from aiogram import Bot

from app.bot.keyboards.common import admin_order_actions
from app.config import get_settings
from app.db.models import Order


def format_order(order: Order) -> str:
    """Текстовое представление заявки для админа."""
    lines = [
        f"🆕 <b>Новая заявка #{order.id}</b>",
        f"👤 {order.user.full_name}",
    ]
    if order.user.username:
        lines.append(f"   @{order.user.username}")
    if order.user.phone:
        lines.append(f"   📱 {order.user.phone}")
    lines.append("")
    for item in order.items:
        lines.append(
            f"• {item.product.name} × {item.quantity} = {item.price * item.quantity:.0f} ₽"
        )
    lines.append("")
    lines.append(f"💰 <b>Итого: {order.total:.0f} ₽</b>")
    if order.comment:
        lines.append(f"💬 {order.comment}")
    return "\n".join(lines)


async def notify_admins_new_order(bot: Bot, order: Order) -> None:
    """Рассылает уведомление о новой заявке всем админам из настроек."""
    text = format_order(order)
    keyboard = admin_order_actions(order.id)
    for admin_id in get_settings().admin_ids:
        try:
            await bot.send_message(admin_id, text, reply_markup=keyboard)
        except Exception:  # noqa: BLE001 — один недоступный админ не должен ронять остальных
            continue
