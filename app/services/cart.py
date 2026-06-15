"""Корзина — чистая доменная логика без обращений к БД (легко тестируется)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CartLine:
    """Одна позиция в корзине."""

    product_id: int
    name: str
    price: float
    quantity: int

    @property
    def subtotal(self) -> float:
        """Стоимость позиции с учётом количества."""
        return round(self.price * self.quantity, 2)


@dataclass
class Cart:
    """Корзина клиента. Хранит позиции и считает итог.

    Чистый объект: не знает ни про БД, ни про Telegram — поэтому его
    легко покрыть юнит-тестами.
    """

    _lines: dict[int, CartLine] = field(default_factory=dict)

    def add(self, product_id: int, name: str, price: float, quantity: int = 1) -> None:
        """Добавляет товар. Если он уже в корзине — увеличивает количество."""
        if quantity <= 0:
            raise ValueError("Количество должно быть больше нуля")
        existing = self._lines.get(product_id)
        new_qty = (existing.quantity if existing else 0) + quantity
        self._lines[product_id] = CartLine(product_id, name, price, new_qty)

    def remove(self, product_id: int) -> None:
        """Полностью убирает товар из корзины."""
        self._lines.pop(product_id, None)

    def set_quantity(self, product_id: int, quantity: int) -> None:
        """Задаёт точное количество. 0 или меньше — удаляет позицию."""
        if quantity <= 0:
            self.remove(product_id)
            return
        line = self._lines[product_id]
        self._lines[product_id] = CartLine(line.product_id, line.name, line.price, quantity)

    def clear(self) -> None:
        """Очищает корзину."""
        self._lines.clear()

    @property
    def lines(self) -> list[CartLine]:
        """Список позиций в порядке добавления."""
        return list(self._lines.values())

    @property
    def total(self) -> float:
        """Итоговая сумма заказа."""
        return round(sum(line.subtotal for line in self._lines.values()), 2)

    @property
    def total_quantity(self) -> int:
        """Общее число единиц товара в корзине."""
        return sum(line.quantity for line in self._lines.values())

    @property
    def is_empty(self) -> bool:
        return not self._lines
