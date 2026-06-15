"""Старт, регистрация клиента, контакты."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Contact, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.common import main_menu, request_phone
from app.bot.states import Registration
from app.config import get_settings
from app.db.repositories import UserRepository

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, session: AsyncSession) -> None:
    """Приветствие. Если клиент новый — запускаем регистрацию."""
    await state.clear()
    assert message.from_user is not None
    users = UserRepository(session)
    user = await users.get_by_telegram_id(message.from_user.id)

    business = get_settings().business_name
    if user is not None:
        await message.answer(
            f"С возвращением, {user.full_name}! 👋\n" f"Добро пожаловать в «{business}».",
            reply_markup=main_menu(),
        )
        return

    await message.answer(
        f"Здравствуйте! 👋\nЭто бот «{business}».\n\nКак вас зовут?",
    )
    await state.set_state(Registration.waiting_for_name)


@router.message(Registration.waiting_for_name, F.text)
async def reg_name(message: Message, state: FSMContext) -> None:
    """Сохраняем имя, просим телефон."""
    name = (message.text or "").strip()
    if len(name) < 2:
        await message.answer("Имя слишком короткое, попробуйте ещё раз.")
        return
    await state.update_data(full_name=name)
    await message.answer(
        "Приятно познакомиться! Оставьте номер телефона, " "чтобы мы могли связаться по заявке.",
        reply_markup=request_phone(),
    )
    await state.set_state(Registration.waiting_for_phone)


@router.message(Registration.waiting_for_phone, F.contact)
async def reg_phone_contact(message: Message, state: FSMContext, session: AsyncSession) -> None:
    """Регистрация по кнопке «Отправить номер»."""
    contact: Contact = message.contact  # type: ignore[assignment]
    await _finish_registration(message, state, session, phone=contact.phone_number)


@router.message(Registration.waiting_for_phone, F.text)
async def reg_phone_text(message: Message, state: FSMContext, session: AsyncSession) -> None:
    """Регистрация, если номер ввели текстом (или пропустили)."""
    text = (message.text or "").strip()
    phone = None if text.lower() in {"пропустить", "skip", "-"} else text
    await _finish_registration(message, state, session, phone=phone)


async def _finish_registration(
    message: Message, state: FSMContext, session: AsyncSession, phone: str | None
) -> None:
    """Создаёт пользователя и завершает регистрацию."""
    assert message.from_user is not None
    data = await state.get_data()
    users = UserRepository(session)
    user = await users.create(
        telegram_id=message.from_user.id,
        full_name=data["full_name"],
        username=message.from_user.username,
    )
    user.phone = phone
    await session.commit()
    await state.clear()
    await message.answer(
        "Готово! Регистрация завершена. ✅\nВыберите действие в меню ниже.",
        reply_markup=main_menu(),
    )


@router.message(F.text == "📞 Контакты")
async def contacts(message: Message) -> None:
    """Контактная информация бизнеса."""
    business = get_settings().business_name
    await message.answer(
        f"<b>{business}</b>\n\n"
        "📍 Адрес: укажите в настройках\n"
        "🕐 Часы работы: 9:00 – 21:00\n"
        "📱 Телефон: +7 (000) 000-00-00\n\n"
        "Мы всегда рады вам! 🙌"
    )
