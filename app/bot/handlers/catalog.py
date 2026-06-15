"""Просмотр каталога и добавление товаров в корзину."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.cart_storage import get_cart
from app.bot.keyboards.common import product_card
from app.services.catalog import CatalogService

router = Router()


@router.message(F.text == "🛍 Каталог")
async def show_catalog(message: Message, session: AsyncSession) -> None:
    """Показывает активные товары карточками."""
    catalog = CatalogService(session)
    products = await catalog.list_active()
    if not products:
        await message.answer("Каталог пока пуст. Загляните позже 🙂")
        return

    await message.answer("Наш каталог:")
    for product in products:
        caption = f"<b>{product.name}</b>\n"
        if product.description:
            caption += f"{product.description}\n"
        caption += f"\n💰 {product.price:.0f} ₽"
        if product.photo_url:
            await message.answer_photo(
                product.photo_url, caption=caption, reply_markup=product_card(product)
            )
        else:
            await message.answer(caption, reply_markup=product_card(product))


@router.callback_query(F.data.startswith("add:"))
async def add_to_cart(callback: CallbackQuery, session: AsyncSession) -> None:
    """Добавляет товар в корзину клиента."""
    assert callback.data is not None
    product_id = int(callback.data.split(":")[1])

    catalog = CatalogService(session)
    product = await catalog.get(product_id)
    if product is None or not product.is_active:
        await callback.answer("Товар недоступен", show_alert=True)
        return

    cart = get_cart(callback.from_user.id)
    cart.add(product.id, product.name, float(product.price))
    await callback.answer(f"«{product.name}» в корзине 🛒")
