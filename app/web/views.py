"""Общий объект шаблонов Jinja2 и вспомогательные хелперы для веба."""

from __future__ import annotations

from pathlib import Path

from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.db.models import OrderStatus

_TEMPLATES_DIR = Path(__file__).parent / "templates"

# Человекочитаемые подписи и цвет-классы статусов (новая тема)
STATUS_META: dict[OrderStatus, tuple[str, str]] = {
    OrderStatus.NEW: ("Новая", "blue"),
    OrderStatus.IN_PROGRESS: ("В работе", "orange"),
    OrderStatus.DONE: ("Готово", "green"),
    OrderStatus.CANCELLED: ("Отменена", "gray"),
}

# Список (value, label) для кнопок-фильтров в шаблонах
STATUS_CHOICES = [(s.value, label) for s, (label, _) in STATUS_META.items()]


def status_badge(status: OrderStatus) -> str:
    """HTML-бейдж статуса для таблиц."""
    label, color = STATUS_META[status]
    return f'<span class="badge-m badge-{color}">{label}</span>'


templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))
templates.env.globals["business_name"] = get_settings().business_name
templates.env.globals["status_badge"] = status_badge
