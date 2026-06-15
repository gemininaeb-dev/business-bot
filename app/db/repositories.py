"""Репозитории — слой доступа к данным. Только запросы к БД, без бизнес-логики."""

from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Order, OrderItem, OrderStatus, Product, User


class UserRepository:
    """Доступ к таблице пользователей."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        result = await self.session.execute(select(User).where(User.telegram_id == telegram_id))
        return result.scalar_one_or_none()

    async def create(self, telegram_id: int, full_name: str, username: str | None) -> User:
        user = User(telegram_id=telegram_id, full_name=full_name, username=username)
        self.session.add(user)
        await self.session.flush()
        return user

    async def count(self) -> int:
        result = await self.session.execute(select(func.count(User.id)))
        return int(result.scalar_one())

    async def all_telegram_ids(self) -> list[int]:
        result = await self.session.execute(select(User.telegram_id))
        return [row[0] for row in result.all()]


class ProductRepository:
    """Доступ к каталогу товаров."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, product_id: int) -> Product | None:
        return await self.session.get(Product, product_id)

    async def list_active(self) -> list[Product]:
        result = await self.session.execute(
            select(Product).where(Product.is_active.is_(True)).order_by(Product.id)
        )
        return list(result.scalars().all())

    async def list_all(self) -> list[Product]:
        result = await self.session.execute(select(Product).order_by(Product.id))
        return list(result.scalars().all())

    async def add(self, product: Product) -> Product:
        self.session.add(product)
        await self.session.flush()
        return product

    async def delete(self, product: Product) -> None:
        await self.session.delete(product)


class OrderRepository:
    """Доступ к заявкам."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, order_id: int) -> Order | None:
        result = await self.session.execute(
            select(Order)
            .where(Order.id == order_id)
            .options(
                selectinload(Order.user),
                selectinload(Order.items).selectinload(OrderItem.product),
            )
        )
        return result.scalar_one_or_none()

    async def add(self, order: Order) -> Order:
        self.session.add(order)
        await self.session.flush()
        return order

    async def list_filtered(self, status: OrderStatus | None = None) -> list[Order]:
        query = (
            select(Order)
            .options(
                selectinload(Order.user),
                selectinload(Order.items).selectinload(OrderItem.product),
            )
            .order_by(Order.created_at.desc())
        )
        if status is not None:
            query = query.where(Order.status == status)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_since(self, since: datetime) -> int:
        result = await self.session.execute(
            select(func.count(Order.id)).where(Order.created_at >= since)
        )
        return int(result.scalar_one())

    async def revenue_since(self, since: datetime) -> float:
        result = await self.session.execute(
            select(func.coalesce(func.sum(Order.total), 0)).where(
                Order.created_at >= since, Order.status == OrderStatus.DONE
            )
        )
        return float(result.scalar_one())

    async def stats_last_days(self, days: int = 7) -> dict[str, int | float]:
        since = datetime.utcnow() - timedelta(days=days)
        return {
            "orders": await self.count_since(since),
            "revenue": await self.revenue_since(since),
        }
