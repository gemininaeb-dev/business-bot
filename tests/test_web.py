"""Smoke-тесты веб-панели через TestClient.

Проверяют, что приложение поднимается, защита работает, а вход даёт
доступ к страницам. Используется отдельная in-memory БД.
"""

import os
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

# Настройки до импорта приложения
os.environ.setdefault("BOT_TOKEN", "123:test")
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["ADMIN_LOGIN"] = "admin"
os.environ["ADMIN_PASSWORD"] = "secret"
os.environ["SECRET_KEY"] = "test-secret"


@pytest.fixture
def client() -> Iterator[TestClient]:
    from app.web.app import create_app

    with TestClient(create_app()) as c:
        yield c


def test_login_page_opens(client: TestClient) -> None:
    resp = client.get("/login")
    assert resp.status_code == 200
    assert "Вход" in resp.text


def test_protected_redirects_to_login(client: TestClient) -> None:
    resp = client.get("/orders", follow_redirects=False)
    assert resp.status_code == 303
    assert resp.headers["location"] == "/login"


def test_wrong_credentials_rejected(client: TestClient) -> None:
    resp = client.post(
        "/login", data={"login": "admin", "password": "nope"}, follow_redirects=False
    )
    assert resp.status_code == 401


def test_login_and_browse(client: TestClient) -> None:
    resp = client.post(
        "/login",
        data={"login": "admin", "password": "secret"},
        follow_redirects=False,
    )
    assert resp.status_code == 303

    # после входа доступны защищённые страницы
    assert client.get("/").status_code == 200
    assert client.get("/orders").status_code == 200
    assert client.get("/products").status_code == 200


def test_import_demo_products(client: TestClient) -> None:
    client.post("/login", data={"login": "admin", "password": "secret"})
    client.post("/products/import")
    page = client.get("/products")
    assert "Латте" in page.text
