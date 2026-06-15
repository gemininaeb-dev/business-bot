"""Тесты сервисов каталога и заявок на in-memory БД."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import OrderStatus
from app.db.repositories import UserRepository
from app.services.cart import Cart
from app.services.catalog import CatalogService
from app.services.orders import OrderService


async def test_create_product(session: AsyncSession) -> None:
    catalog = CatalogService(session)
    product = await catalog.create(name="Латте", price=250.0, description="Вкусно")
    assert product.id is not None
    assert product.is_active is True
    assert len(await catalog.list_active()) == 1


async def test_create_product_empty_name_raises(session: AsyncSession) -> None:
    catalog = CatalogService(session)
    with pytest.raises(ValueError):
        await catalog.create(name="   ", price=100.0)


async def test_toggle_active_hides_from_catalog(session: AsyncSession) -> None:
    catalog = CatalogService(session)
    product = await catalog.create(name="Чай", price=150.0)
    await catalog.toggle_active(product.id)
    assert await catalog.list_active() == []
    assert len(await catalog.list_all()) == 1


async def test_create_order_from_cart(session: AsyncSession) -> None:
    # регистрируем клиента
    users = UserRepository(session)
    await users.create(telegram_id=555, full_name="Иван", username="ivan")
    await session.commit()

    catalog = CatalogService(session)
    p1 = await catalog.create(name="Латте", price=250.0)
    p2 = await catalog.create(name="Круассан", price=120.0)

    cart = Cart()
    cart.add(p1.id, p1.name, float(p1.price), quantity=2)
    cart.add(p2.id, p2.name, float(p2.price))

    orders = OrderService(session)
    order = await orders.create_from_cart(555, cart, comment="Без сахара")

    assert order.total == 620.0
    assert order.status == OrderStatus.NEW
    assert len(order.items) == 2
    assert order.comment == "Без сахара"
    # товар должен быть загружен заранее (иначе MissingGreenlet при рендере)
    assert {item.product.name for item in order.items} == {"Латте", "Круассан"}


async def test_empty_cart_cannot_be_ordered(session: AsyncSession) -> None:
    users = UserRepository(session)
    await users.create(telegram_id=1, full_name="Тест", username=None)
    await session.commit()

    orders = OrderService(session)
    with pytest.raises(ValueError):
        await orders.create_from_cart(1, Cart())


async def test_change_order_status(session: AsyncSession) -> None:
    users = UserRepository(session)
    await users.create(telegram_id=7, full_name="Пётр", username=None)
    await session.commit()

    catalog = CatalogService(session)
    p = await catalog.create(name="Эспрессо", price=180.0)
    cart = Cart()
    cart.add(p.id, p.name, float(p.price))

    orders = OrderService(session)
    order = await orders.create_from_cart(7, cart)
    updated = await orders.change_status(order.id, OrderStatus.DONE)

    assert updated is not None
    assert updated.status == OrderStatus.DONE


async def test_stats_counts_clients(session: AsyncSession) -> None:
    users = UserRepository(session)
    await users.create(telegram_id=1, full_name="A", username=None)
    await users.create(telegram_id=2, full_name="B", username=None)
    await session.commit()

    orders = OrderService(session)
    stats = await orders.stats()
    assert stats["clients"] == 2
