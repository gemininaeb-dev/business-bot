"""Тесты чистой логики корзины."""

import pytest

from app.services.cart import Cart


def test_add_single_item() -> None:
    cart = Cart()
    cart.add(product_id=1, name="Латте", price=250.0)
    assert cart.total == 250.0
    assert cart.total_quantity == 1
    assert not cart.is_empty


def test_add_same_item_increases_quantity() -> None:
    cart = Cart()
    cart.add(1, "Латте", 250.0)
    cart.add(1, "Латте", 250.0, quantity=2)
    assert cart.total_quantity == 3
    assert cart.total == 750.0
    assert len(cart.lines) == 1


def test_total_sums_multiple_products() -> None:
    cart = Cart()
    cart.add(1, "Латте", 250.0, quantity=2)
    cart.add(2, "Круассан", 120.0)
    assert cart.total == 620.0
    assert cart.total_quantity == 3


def test_set_quantity_to_zero_removes_line() -> None:
    cart = Cart()
    cart.add(1, "Латте", 250.0)
    cart.set_quantity(1, 0)
    assert cart.is_empty


def test_remove_item() -> None:
    cart = Cart()
    cart.add(1, "Латте", 250.0)
    cart.add(2, "Чай", 150.0)
    cart.remove(1)
    assert cart.total == 150.0
    assert len(cart.lines) == 1


def test_clear() -> None:
    cart = Cart()
    cart.add(1, "Латте", 250.0)
    cart.clear()
    assert cart.is_empty
    assert cart.total == 0


def test_add_zero_quantity_raises() -> None:
    cart = Cart()
    with pytest.raises(ValueError):
        cart.add(1, "Латте", 250.0, quantity=0)


def test_subtotal_rounding() -> None:
    cart = Cart()
    cart.add(1, "Кофе", 99.99, quantity=3)
    assert cart.lines[0].subtotal == 299.97
