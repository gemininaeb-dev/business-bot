# 🛍 Business Bot — Telegram-бот для бизнеса + веб-панель

Готовое решение для малого бизнеса (кафе, салон, магазин, сервис): клиенты
оформляют заявки в Telegram-боте, а владелец управляет каталогом и заявками
через удобную веб-панель.

Проект показывает полный цикл: **Telegram-бот + REST-бэкенд + веб-интерфейс +
база данных + парсинг + тесты + Docker-деплой**.

---

## ✨ Возможности

### Telegram-бот (для клиентов)
- 👤 Регистрация с сохранением имени и телефона
- 🛍 Каталог товаров с фото, описанием и ценой
- 🛒 Корзина: добавление, подсчёт суммы, оформление заявки
- 📋 История своих заявок и их статусы
- 🔔 Уведомления администратору о каждой новой заявке (с кнопками смены статуса)

### Веб-панель (для владельца)
- 🔐 Авторизация по логину/паролю (сессионные cookie)
- 📊 Дашборд: клиенты, заявки и выручка за 7 дней
- 📝 Заявки с фильтром по статусам и сменой статуса в один клик
- 📦 Управление каталогом: добавление, скрытие, удаление товаров
- 📣 Массовая рассылка по базе клиентов
- ⬇️ Импорт товаров из прайс-листа (парсер на BeautifulSoup)

---

## 🧰 Стек технологий

| Слой | Технологии |
|------|-----------|
| Бот | [aiogram 3](https://docs.aiogram.dev/) (async, FSM, middlewares) |
| Веб | [FastAPI](https://fastapi.tiangolo.com/) + Jinja2 + Bootstrap 5 |
| База данных | SQLAlchemy 2 (async) · SQLite / PostgreSQL |
| Парсинг | BeautifulSoup4 + httpx |
| Качество | pytest · mypy · ruff · black |
| Деплой | Docker · Railway |

---

## 🏗 Архитектура

Чистое разделение слоёв — бизнес-логика не зависит ни от Telegram, ни от веба,
поэтому легко тестируется и переиспользуется обоими интерфейсами.

```
app/
├── bot/         # Telegram: handlers, keyboards, FSM, middlewares
├── web/         # FastAPI: routes, templates, security
├── services/    # бизнес-логика (cart, catalog, orders) — без I/O
├── db/          # модели, сессии, репозитории
├── parser/      # импорт товаров (BeautifulSoup)
└── config.py    # настройки из .env (pydantic-settings)
tests/           # pytest: services, парсер, веб (TestClient)
```

Один поток данных, две точки входа (бот и панель), общая БД.

---

## 🚀 Быстрый старт

### 1. Установка
```bash
git clone <repo-url>
cd business-bot
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/macOS
pip install -r requirements.txt
```

### 2. Настройка
Скопируйте `.env.example` в `.env` и заполните:
```bash
cp .env.example .env
```
Минимум — токен бота от [@BotFather](https://t.me/BotFather) и ваш Telegram ID
в `ADMIN_IDS` (узнать можно у [@userinfobot](https://t.me/userinfobot)).

### 3. Запуск
```bash
python main.py
```
- Бот стартует на long-polling
- Веб-панель: http://localhost:8000 (логин/пароль из `.env`)

> Первый запуск создаёт SQLite-базу автоматически. Чтобы быстро наполнить
> каталог — в панели нажмите «Импортировать демо-товары».

---

## 🐳 Деплой (Docker / Railway)

```bash
docker build -t business-bot .
docker run --env-file .env -p 8000:8000 business-bot
```

Или в один клик на [Railway](https://railway.app): подключите репозиторий,
задайте переменные окружения из `.env.example` — `railway.json` и `Dockerfile`
уже настроены. Порт хостинга подхватывается автоматически через `PORT`.

---

## ✅ Качество кода

```bash
pip install -r requirements-dev.txt

pytest            # тесты (services, парсер, веб)
mypy app main.py  # статическая типизация
ruff check .      # линтер
black --check .   # форматирование
```

Весь код типизирован, отформатирован и покрыт тестами на бизнес-логику.

---

## 📌 Возможные доработки
- Онлайн-оплата (ЮKassa / Telegram Payments)
- Перенос корзины и FSM в Redis
- Роли администраторов и журнал действий
- Экспорт заявок в Excel / Google Sheets

---

*Проект демонстрирует навыки backend-разработки на Python: асинхронность,
чистую архитектуру, работу с БД, веб и автоматизацию.*
