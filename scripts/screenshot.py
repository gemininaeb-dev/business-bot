"""Снимает скриншоты веб-панели для README (Playwright).

Запуск (сервер должен быть запущен на :8000):
    python -m scripts.screenshot
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from playwright.async_api import async_playwright

BASE = "http://127.0.0.1:8000"
LOGIN = "admin"
PASSWORD = "Business2026!"
OUT = Path("docs/screenshots")

# (путь, имя файла, пауза мс — чтобы дождаться анимации счётчиков)
PAGES = [
    ("/", "dashboard.png", 1600),
    ("/orders", "orders.png", 400),
    ("/orders/1", "order_detail.png", 400),
    ("/products", "products.png", 400),
    ("/broadcast", "broadcast.png", 400),
]


async def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()

        # --- Десктоп ---
        ctx = await browser.new_context(
            viewport={"width": 1440, "height": 900}, device_scale_factor=2
        )
        page = await ctx.new_page()

        # страница логина (до входа)
        await page.goto(f"{BASE}/login")
        await page.wait_for_timeout(500)
        await page.screenshot(path=str(OUT / "login.png"))

        # вход
        await page.fill('input[name="login"]', LOGIN)
        await page.fill('input[name="password"]', PASSWORD)
        await page.click('button[type="submit"]')
        await page.wait_for_url(f"{BASE}/")

        for path, name, pause in PAGES:
            await page.goto(f"{BASE}{path}")
            await page.wait_for_timeout(pause)
            await page.screenshot(path=str(OUT / name))
            print(f"  [ok] {name}")
        await ctx.close()

        # --- Мобильная версия (адаптив) ---
        mctx = await browser.new_context(
            viewport={"width": 390, "height": 844}, device_scale_factor=2
        )
        mpage = await mctx.new_page()
        await mpage.goto(f"{BASE}/login")
        await mpage.fill('input[name="login"]', LOGIN)
        await mpage.fill('input[name="password"]', PASSWORD)
        await mpage.click('button[type="submit"]')
        await mpage.wait_for_url(f"{BASE}/")
        await mpage.wait_for_timeout(1600)
        await mpage.screenshot(path=str(OUT / "mobile_dashboard.png"))
        print("  [ok] mobile_dashboard.png")
        await mctx.close()

        await browser.close()
    print(f"Готово. Скриншоты в {OUT}")


if __name__ == "__main__":
    asyncio.run(main())
