"""Корзина и оформление заявки."""

from __future__ import annotations

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.cart_storage import clear_cart, get_cart
from app.bot.keyboards.common import cart_actions, confirm_order, main_menu
from app.bot.notify import notify_admins_new_order
from app.bot.states import Checkout
from app.services.orders import OrderService

router = Router()


def _render_cart(telegram_id: int) -> str:
    """Текстовое представление корзины."""
    cart = get_cart(telegram_id)
    if cart.is_empty:
        return "Ваша корзина пуста 🛒"
    lines = ["<b>🛒 Ваша корзина:</b>", ""]
    for line in cart.lines:
        lines.append(f"• {line.name} × {line.quantity} = {line.subtotal:.0f} ₽")
    lines.append("")
    lines.append(f"💰 <b>Итого: {cart.total:.0f} ₽</b>")
    return "\n".join(lines)


@router.message(F.text == "🛒 Корзина")
async def show_cart(message: Message) -> None:
    """Показывает содержимое корзины."""
    assert message.from_user is not None
    cart = get_cart(message.from_user.id)
    if cart.is_empty:
        await message.answer("Ваша корзина пуста 🛒\nЗагляните в каталог!")
        return
    await message.answer(_render_cart(message.from_user.id), reply_markup=cart_actions())


@router.callback_query(F.data == "clear_cart")
async def cart_clear(callback: CallbackQuery) -> None:
    """Очищает корзину."""
    clear_cart(callback.from_user.id)
    await callback.answer("Корзина очищена")
    if callback.message:
        await callback.message.answer("Корзина очищена 🗑", reply_markup=main_menu())


@router.callback_query(F.data == "checkout")
async def checkout_start(callback: CallbackQuery, state: FSMContext) -> None:
    """Начинает оформление: просим комментарий."""
    cart = get_cart(callback.from_user.id)
    if cart.is_empty:
        await callback.answer("Корзина пуста", show_alert=True)
        return
    await callback.answer()
    if callback.message:
        await callback.message.answer(
            "Добавьте комментарий к заявке (например, время или пожелания).\n"
            "Или отправьте «-», чтобы пропустить."
        )
    await state.set_state(Checkout.waiting_for_comment)


@router.message(Checkout.waiting_for_comment, F.text)
async def checkout_comment(message: Message, state: FSMContext) -> None:
    """Сохраняем комментарий, показываем подтверждение."""
    assert message.from_user is not None
    text = (message.text or "").strip()
    comment = "" if text == "-" else text
    await state.update_data(comment=comment)

    summary = _render_cart(message.from_user.id)
    if comment:
        summary += f"\n\n💬 {comment}"
    await message.answer(f"{summary}\n\nПодтвердить заявку?", reply_markup=confirm_order())
    await state.set_state(Checkout.confirming)


@router.callback_query(Checkout.confirming, F.data == "confirm")
async def checkout_confirm(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession, bot: Bot
) -> None:
    """Создаёт заявку из корзины и уведомляет админов."""
    data = await state.get_data()
    cart = get_cart(callback.from_user.id)

    orders = OrderService(session)
    try:
        order = await orders.create_from_cart(
            callback.from_user.id, cart, comment=data.get("comment", "")
        )
    except ValueError as exc:
        await callback.answer(str(exc), show_alert=True)
        await state.clear()
        return

    clear_cart(callback.from_user.id)
    await state.clear()
    await callback.answer("Заявка оформлена!")
    if callback.message:
        await callback.message.answer(
            f"Спасибо! Заявка №{order.id} принята ✅\n" "Мы свяжемся с вами в ближайшее время.",
            reply_markup=main_menu(),
        )
    await notify_admins_new_order(bot, order)


@router.callback_query(Checkout.confirming, F.data == "cancel")
async def checkout_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    """Отмена оформления (корзина сохраняется)."""
    await state.clear()
    await callback.answer("Оформление отменено")
    if callback.message:
        await callback.message.answer(
            "Оформление отменено. Корзина сохранена.", reply_markup=main_menu()
        )
