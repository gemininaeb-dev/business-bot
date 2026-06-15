"""Наполнение базы демо-данными для скриншотов и презентации.

Создаёт несколько клиентов и заявок с разными статусами, если их ещё нет.
Запуск:  python -m scripts.seed_demo
"""

from __future__ import annotations

import asyncio
import random

from app.db.models import Order, OrderItem, OrderStatus, User
from app.db.repositories import ProductRepository
from app.db.session import get_sessionmaker, init_db
from app.parser.products_parser import parse_demo_menu
from app.services.catalog import CatalogService

_CLIENTS = [
    ("Анна Смирнова", "anna_s", "+7 916 123-45-67"),
    ("Дмитрий Орлов", "dmitry_orlov", "+7 925 987-65-43"),
    ("Мария Кузнецова", "mkuznetsova", "+7 903 555-22-11"),
    ("Игорь Петров", "igor_p", None),
]

_STATUSES = [
    OrderStatus.NEW,
    OrderStatus.NEW,
    OrderStatus.IN_PROGRESS,
    OrderStatus.DONE,
    OrderStatus.DONE,
    OrderStatus.DONE,
]


async def main() -> None:
    await init_db()
    maker = get_sessionmaker()

    async with maker() as session:
        # каталог: если пуст — импортируем демо-товары парсером
        catalog = CatalogService(session)
        if not await catalog.list_all():
            await catalog.import_parsed(parse_demo_menu())

        products = await ProductRepository(session).list_active()
        if not products:
            print("Нет товаров — нечего класть в заявки")
            return

        # клиенты (telegram_id с большим оффсетом, чтобы не пересечься с реальными)
        users: list[User] = []
        for i, (name, username, phone) in enumerate(_CLIENTS):
            tg_id = 900000000 + i
            user = User(telegram_id=tg_id, full_name=name, username=username, phone=phone)
            session.add(user)
            users.append(user)
        await session.flush()

        # заявки с разными статусами
        rnd = random.Random(42)
        for status in _STATUSES:
            user = rnd.choice(users)
            chosen = rnd.sample(products, k=rnd.randint(1, 3))
            items = [
                OrderItem(
                    product_id=p.id,
                    quantity=rnd.randint(1, 3),
                    price=float(p.price),
                )
                for p in chosen
            ]
            total = sum(it.price * it.quantity for it in items)
            session.add(Order(user=user, status=status, total=total, comment="", items=items))

        await session.commit()
        print(f"Добавлено клиентов: {len(users)}, заявок: {len(_STATUSES)}")


if __name__ == "__main__":
    asyncio.run(main())
