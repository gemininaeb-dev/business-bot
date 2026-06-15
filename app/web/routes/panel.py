"""Основные страницы админ-панели: дашборд, заявки, каталог, рассылка."""

from __future__ import annotations

from contextlib import suppress

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.bot import create_bot
from app.db.models import OrderStatus
from app.db.repositories import UserRepository
from app.db.session import get_session
from app.parser.products_parser import parse_demo_menu
from app.services.catalog import CatalogService
from app.services.orders import OrderService
from app.web.security import auth_required
from app.web.views import STATUS_CHOICES, templates

router = APIRouter(dependencies=[Depends(auth_required)])


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, session: AsyncSession = Depends(get_session)) -> HTMLResponse:
    orders = OrderService(session)
    stats = await orders.stats(days=7)
    recent = (await orders.list_filtered())[:8]
    new_orders = len(await orders.list_filtered(OrderStatus.NEW))
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {"stats": stats, "recent": recent, "new_orders": new_orders},
    )


@router.get("/orders", response_class=HTMLResponse)
async def orders_list(
    request: Request,
    status: str | None = None,
    session: AsyncSession = Depends(get_session),
) -> HTMLResponse:
    filter_status = OrderStatus(status) if status else None
    orders = OrderService(session)
    items = await orders.list_filtered(filter_status)
    return templates.TemplateResponse(
        request,
        "orders.html",
        {
            "orders": items,
            "statuses": STATUS_CHOICES,
            "current_status": status,
        },
    )


@router.get("/orders/{order_id}", response_class=HTMLResponse, response_model=None)
async def order_detail(
    request: Request,
    order_id: int,
    session: AsyncSession = Depends(get_session),
) -> HTMLResponse | RedirectResponse:
    order = await OrderService(session).get(order_id)
    if order is None:
        return RedirectResponse("/orders", status_code=303)
    return templates.TemplateResponse(
        request,
        "order_detail.html",
        {"order": order, "statuses": STATUS_CHOICES},
    )


@router.post("/orders/{order_id}/status")
async def order_change_status(
    order_id: int,
    status: str = Form(...),
    session: AsyncSession = Depends(get_session),
) -> RedirectResponse:
    await OrderService(session).change_status(order_id, OrderStatus(status))
    return RedirectResponse(f"/orders/{order_id}", status_code=303)


@router.get("/products", response_class=HTMLResponse)
async def products_list(
    request: Request, session: AsyncSession = Depends(get_session)
) -> HTMLResponse:
    products = await CatalogService(session).list_all()
    return templates.TemplateResponse(request, "products.html", {"products": products})


@router.post("/products")
async def product_create(
    name: str = Form(...),
    price: float = Form(...),
    description: str = Form(""),
    photo_url: str = Form(""),
    session: AsyncSession = Depends(get_session),
) -> RedirectResponse:
    with suppress(ValueError):
        await CatalogService(session).create(
            name=name,
            price=price,
            description=description,
            photo_url=photo_url or None,
        )
    return RedirectResponse("/products", status_code=303)


@router.post("/products/import")
async def products_import(
    session: AsyncSession = Depends(get_session),
) -> RedirectResponse:
    """Импортирует демо-товары через парсер (BeautifulSoup)."""
    await CatalogService(session).import_parsed(parse_demo_menu())
    return RedirectResponse("/products", status_code=303)


@router.post("/products/{product_id}/toggle")
async def product_toggle(
    product_id: int, session: AsyncSession = Depends(get_session)
) -> RedirectResponse:
    await CatalogService(session).toggle_active(product_id)
    return RedirectResponse("/products", status_code=303)


@router.post("/products/{product_id}/delete")
async def product_delete(
    product_id: int, session: AsyncSession = Depends(get_session)
) -> RedirectResponse:
    await CatalogService(session).delete(product_id)
    return RedirectResponse("/products", status_code=303)


@router.get("/broadcast", response_class=HTMLResponse)
async def broadcast_form(
    request: Request, session: AsyncSession = Depends(get_session)
) -> HTMLResponse:
    recipients = await UserRepository(session).count()
    return templates.TemplateResponse(
        request,
        "broadcast.html",
        {"recipients": recipients, "sent": None, "total": 0},
    )


@router.post("/broadcast", response_class=HTMLResponse)
async def broadcast_send(
    request: Request,
    text: str = Form(...),
    session: AsyncSession = Depends(get_session),
) -> HTMLResponse:
    user_ids = await UserRepository(session).all_telegram_ids()
    bot = create_bot()
    sent = 0
    try:
        for uid in user_ids:
            try:
                await bot.send_message(uid, text)
                sent += 1
            except Exception:  # noqa: BLE001
                continue
    finally:
        await bot.session.close()
    return templates.TemplateResponse(
        request,
        "broadcast.html",
        {"recipients": len(user_ids), "sent": sent, "total": len(user_ids)},
    )
