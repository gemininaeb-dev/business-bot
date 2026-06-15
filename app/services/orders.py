"""Сервис заявок — создание заказа из корзины, смена статуса, статистика."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Order, OrderItem, OrderStatus
from app.db.repositories import OrderRepository, UserRepository
from app.services.cart import Cart


class OrderService:
    """Бизнес-операции с заявками."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.orders = OrderRepository(session)
        self.users = UserRepository(session)

    async def create_from_cart(self, telegram_id: int, cart: Cart, comment: str = "") -> Order:
        """Создаёт заявку из корзины клиента.

        Корзина должна быть непустой, а клиент — зарегистрированным.
        """
        if cart.is_empty:
            raise ValueError("Нельзя оформить пустую корзину")

        user = await self.users.get_by_telegram_id(telegram_id)
        if user is None:
            raise ValueError("Клиент не зарегистрирован")

        order = Order(
            user_id=user.id,
            comment=comment.strip(),
            total=cart.total,
            items=[
                OrderItem(
                    product_id=line.product_id,
                    quantity=line.quantity,
                    price=line.price,
                )
                for line in cart.lines
            ],
        )
        await self.orders.add(order)
        await self.session.commit()
        return await self.orders.get(order.id)  # type: ignore[return-value]

    async def get(self, order_id: int) -> Order | None:
        return await self.orders.get(order_id)

    async def list_filtered(self, status: OrderStatus | None = None) -> list[Order]:
        return await self.orders.list_filtered(status)

    async def change_status(self, order_id: int, status: OrderStatus) -> Order | None:
        """Меняет статус заявки."""
        order = await self.orders.get(order_id)
        if order is None:
            return None
        order.status = status
        await self.session.commit()
        return order

    async def stats(self, days: int = 7) -> dict[str, int | float]:
        """Сводная статистика за последние N дней + всего клиентов."""
        data = await self.orders.stats_last_days(days)
        data["clients"] = await self.users.count()
        return data
