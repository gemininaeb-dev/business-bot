"""Маршруты входа и выхода из админ-панели."""

from __future__ import annotations

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.web.security import check_credentials, login_session, logout_session
from app.web.views import templates

router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "login.html", {"error": None})


@router.post("/login", response_model=None)
async def login_submit(
    request: Request,
    login: str = Form(...),
    password: str = Form(...),
) -> RedirectResponse | HTMLResponse:
    if check_credentials(login, password):
        login_session(request)
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse(
        request, "login.html", {"error": "Неверный логин или пароль"}, status_code=401
    )


@router.get("/logout")
async def logout(request: Request) -> RedirectResponse:
    logout_session(request)
    return RedirectResponse("/login", status_code=303)
