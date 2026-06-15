"""Парсер прайс-листа поставщика (BeautifulSoup).

Демонстрирует навык веб-скрапинга. Умеет:
  • разобрать HTML по URL (httpx) либо переданную строку HTML;
  • вытащить товары из разметки в структуру ParsedProduct.

Для надёжного демо есть встроенный образец sample_menu.html и функция
parse_demo_menu(), которая не зависит от внешней сети.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

_SAMPLE_FILE = Path(__file__).parent / "sample_menu.html"


@dataclass(frozen=True)
class ParsedProduct:
    """Распаршенный товар из прайс-листа."""

    name: str
    price: float
    description: str = ""


def parse_html(html: str) -> list[ParsedProduct]:
    """Извлекает товары из HTML вида <div class="item" data-name=... data-price=...>."""
    soup = BeautifulSoup(html, "html.parser")
    products: list[ParsedProduct] = []
    for node in soup.select("div.item"):
        name = (node.get("data-name") or "").strip()
        price_raw = node.get("data-price") or ""
        if not name or not price_raw:
            continue
        try:
            price = float(price_raw)
        except ValueError:
            continue
        desc_node = node.select_one(".desc")
        description = desc_node.get_text(strip=True) if desc_node else ""
        products.append(ParsedProduct(name=name, price=price, description=description))
    return products


async def parse_url(url: str, timeout: float = 10.0) -> list[ParsedProduct]:
    """Скачивает страницу и парсит товары."""
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get(url)
        response.raise_for_status()
    return parse_html(response.text)


def parse_demo_menu() -> list[ParsedProduct]:
    """Парсит встроенный образец прайс-листа (без обращения к сети)."""
    return parse_html(_SAMPLE_FILE.read_text(encoding="utf-8"))
