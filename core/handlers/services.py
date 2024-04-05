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


@router.callback_query(F.data.startswith("service_1"))
@router.callback_query(F.data.startswith("service_2"))
@router.callback_query(F.data.startswith("service_3"))
@router.callback_query(F.data.startswith("service_4"))
@router.callback_query(F.data.startswith("service_5"))
@router.callback_query(F.data.startswith("service_6"))
async def viewing_projects(call: CallbackQuery):
    data = database.get_service(int(call.data.split("_")[-1]))
    message = f"{data['name']}\n{data['description']}"
    if data["photo_id"] is not None:
        await call.message.answer_photo(data["photo_id"], caption=message,
                                        reply_markup=kbi.menu_service_send(call.data.split("_")[-1], call.from_user.id))
        await call.message.delete()
    else:
        try:
            await call.message.edit_text(message,
                                         reply_markup=kbi.menu_service_send(call.data.split("_")[-1],
                                                                            call.from_user.id))
        except TelegramBadRequest:
            await call.message.answer(message,
                                      reply_markup=kbi.menu_service_send(call.data.split("_")[-1], call.from_user.id))
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


@router.callback_query(F.data.startswith("amounts_"))
async def viewing_projects(call: CallbackQuery):
    data = database.get_service(int(call.data.split("_")[-1]))
    data_btn = database.get_mess("watsapp")
    message = f"{data['name']}\n{data['amount_des']}"
    if data["photo_id"] is not None:
        await call.message.edit_caption(caption=message,
                                        reply_markup=kbi.url_btn_amount(data_btn, call.from_user.id, call.data.split("_")[-1],
                                                                 f"service_{call.data.split('_')[-1]}"))
    else:
        try:
            await call.message.edit_text(message, reply_markup=kbi.url_btn_amount(data_btn, call.from_user.id, call.data.split("_")[-1],
                                                                           f"service_{call.data.split('_')[-1]}"))
        except TelegramBadRequest:
            await call.message.answer(message, reply_markup=kbi.url_btn_amount(data_btn, call.from_user.id, call.data.split("_")[-1],
                                                                        f"service_{call.data.split('_')[-1]}"))
            await call.message.delete()
