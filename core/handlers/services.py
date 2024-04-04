from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, InputMediaPhoto

from core.keyboard import inline as kbi
from core.settings import settings, home, get_chat_id
from core.database import database as database

router = Router()


@router.callback_query(F.data == "services")
async def viewing_projects(call: CallbackQuery):
    try:
        await call.message.edit_text("Выберите интересующую вас услугу", reply_markup=kbi.menu_services())
    except TelegramBadRequest:
        await call.message.answer("Выберите интересующую вас услугу", reply_markup=kbi.menu_services())
        await call.message.delete()


@router.callback_query(F.data.startswith("service_"))
async def viewing_projects(call: CallbackQuery):
    data = database.get_service(int(call.data.split("_")[-1]))
    message = f"{data['name']}\n{data['description']}"
    if data["photo_id"] is not None:
        await call.message.answer_photo(data["photo_id"], caption=message,
                                        reply_markup=kbi.menu_service(call.data.split("_")[-1], call.from_user.id))
        await call.message.delete()
    else:
        try:
            await call.message.edit_text(message, reply_markup=kbi.menu_service(call.data.split("_")[-1], call.from_user.id))
        except TelegramBadRequest:
            await call.message.answer(message, reply_markup=kbi.menu_service(call.data.split("_")[-1], call.from_user.id))
            await call.message.delete()
