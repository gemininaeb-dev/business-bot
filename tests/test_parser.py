"""Тесты парсера прайс-листа."""

from app.parser.products_parser import parse_demo_menu, parse_html


def test_parse_html_basic() -> None:
    html = """
    <div class="item" data-name="Кофе" data-price="200">
      <span class="desc">Ароматный</span>
    </div>
    """
    products = parse_html(html)
    assert len(products) == 1
    assert products[0].name == "Кофе"
    assert products[0].price == 200.0
    assert products[0].description == "Ароматный"


def test_parse_html_skips_invalid() -> None:
    html = """
    <div class="item" data-name="Без цены"></div>
    <div class="item" data-price="100"></div>
    <div class="item" data-name="Плохая цена" data-price="abc"></div>
    """
    assert parse_html(html) == []


def test_parse_demo_menu_loads_samples() -> None:
    products = parse_demo_menu()
    assert len(products) >= 5
    assert all(p.price > 0 for p in products)
    names = {p.name for p in products}
    assert "Латте" in names
