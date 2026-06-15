"""Сервис каталога товаров — операции через репозиторий."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Product
from app.db.repositories import ProductRepository
from app.parser.products_parser import ParsedProduct


class CatalogService:
    """Бизнес-операции с каталогом."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.products = ProductRepository(session)

    async def list_active(self) -> list[Product]:
        return await self.products.list_active()

    async def list_all(self) -> list[Product]:
        return await self.products.list_all()

    async def get(self, product_id: int) -> Product | None:
        return await self.products.get(product_id)

    async def create(
        self,
        name: str,
        price: float,
        description: str = "",
        photo_url: str | None = None,
    ) -> Product:
        """Добавляет товар в каталог с валидацией."""
        name = name.strip()
        if not name:
            raise ValueError("Название товара не может быть пустым")
        if price < 0:
            raise ValueError("Цена не может быть отрицательной")
        product = Product(
            name=name,
            price=price,
            description=description.strip(),
            photo_url=photo_url,
        )
        await self.products.add(product)
        await self.session.commit()
        return product

    async def toggle_active(self, product_id: int) -> Product | None:
        """Включает/выключает показ товара клиентам."""
        product = await self.products.get(product_id)
        if product is None:
            return None
        product.is_active = not product.is_active
        await self.session.commit()
        return product

    async def delete(self, product_id: int) -> bool:
        """Удаляет товар. Возвращает True, если товар существовал."""
        product = await self.products.get(product_id)
        if product is None:
            return False
        await self.products.delete(product)
        await self.session.commit()
        return True

    async def import_parsed(self, parsed: list[ParsedProduct]) -> int:
        """Добавляет распарсенные товары, пропуская уже существующие по имени.

        Возвращает количество реально добавленных товаров.
        """
        existing = {p.name.lower() for p in await self.products.list_all()}
        added = 0
        for item in parsed:
            if item.name.lower() in existing:
                continue
            await self.products.add(
                Product(
                    name=item.name,
                    price=item.price,
                    description=item.description,
                )
            )
            existing.add(item.name.lower())
            added += 1
        await self.session.commit()
        return added
