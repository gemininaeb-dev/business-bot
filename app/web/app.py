"""Сборка FastAPI-приложения админ-панели."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.db.session import init_db
from app.web.routes import auth, panel
from app.web.security import add_session_middleware

_STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Создаёт таблицы БД при старте."""
    await init_db()
    yield


def create_app() -> FastAPI:
    """Создаёт и настраивает приложение FastAPI."""
    app = FastAPI(title="Business Bot — админ-панель", lifespan=_lifespan)
    add_session_middleware(app)
    app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")
    app.include_router(auth.router)
    app.include_router(panel.router)
    return app


app = create_app()
