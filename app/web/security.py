"""Авторизация админ-панели через сессионные cookie."""

from __future__ import annotations

import secrets

from fastapi import HTTPException, Request, status
from starlette.middleware.sessions import SessionMiddleware

from app.config import get_settings

_SESSION_KEY = "is_admin"


def add_session_middleware(app: object) -> None:
    """Подключает middleware сессий к приложению FastAPI."""
    app.add_middleware(  # type: ignore[attr-defined]
        SessionMiddleware,
        secret_key=get_settings().secret_key,
        https_only=False,
    )


def check_credentials(login: str, password: str) -> bool:
    """Сравнивает логин/пароль с настройками (защита от timing-атак)."""
    settings = get_settings()
    login_ok = secrets.compare_digest(login, settings.admin_login)
    password_ok = secrets.compare_digest(password, settings.admin_password)
    return login_ok and password_ok


def login_session(request: Request) -> None:
    """Помечает сессию как авторизованную."""
    request.session[_SESSION_KEY] = True


def logout_session(request: Request) -> None:
    """Сбрасывает авторизацию."""
    request.session.pop(_SESSION_KEY, None)


def is_authenticated(request: Request) -> bool:
    """Проверяет, авторизован ли запрос."""
    return bool(request.session.get(_SESSION_KEY))


def auth_required(request: Request) -> None:
    """Зависимость FastAPI: пускает дальше только авторизованных.

    Неавторизованных перенаправляет на /login (303 + заголовок Location).
    """
    if not is_authenticated(request):
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": "/login"},
        )
