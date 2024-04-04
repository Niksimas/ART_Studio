import os

from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, FSInputFile

from core.settings import home
from core.database import database
from core.keyboard import inline_admin as kbi_a
from core.keyboard import inline as kbi

subrouter = Router()


# #################################################################################################################### #
# ############################################# СОЗДАНИЕ УСЛУГ ####################################################### #
# #################################################################################################################### #
class AddProject(StatesGroup):
    SetName = State()
    SetDescription = State()
    SetAmountDescription = State()
    CheckProject = State()


@subrouter.callback_query(F.data == "no", AddProject.CheckProject)
@subrouter.callback_query(F.data == "add_service")
async def set_name_project(call: CallbackQuery, state: FSMContext):
    msg = await call.message.edit_text("Напишите название услуги:", reply_markup=kbi_a.cancel_admin())
    await state.update_data({"del": msg.message_id})
    await state.set_state(AddProject.SetName)


@subrouter.message(AddProject.SetName)
async def set_description_project(mess: Message, state: FSMContext, bot: Bot):
    try:
        del_kb = (await state.get_data())["del"]
        await bot.edit_message_reply_markup(mess.chat.id, del_kb, reply_markup=None)
    except (KeyError, TelegramBadRequest):
        pass
    msg = await mess.answer("Прикрепите фотографию (по желанию) и напишите описание проекта с нужным форматированием",
                            reply_markup=kbi_a.cancel_admin())
    await state.update_data({"name": mess.html_text, "del": msg.message_id})
    await state.set_state(AddProject.SetDescription)


@subrouter.message(AddProject.SetDescription)
async def set_amount_description_project(mess: Message, state: FSMContext, bot: Bot):
    try:
        del_kb = (await state.get_data())["del"]
        await bot.edit_message_reply_markup(mess.chat.id, del_kb, reply_markup=None)
    except (KeyError, TelegramBadRequest):
        pass
    if mess.photo is not None:
        await state.update_data({"photo_id": mess.photo[-1].file_id})
    else:
        await state.update_data({"photo_id": None})
    msg = await mess.answer("Укажите прайс-лист для данной услуги:\n"
                            "Например: \n"
                            "Абонемент на 3 занятия: 3500р.",
                            reply_markup=kbi_a.cancel_admin())
    await state.update_data({"description": mess.html_text, "del": msg.message_id})
    await state.set_state(AddProject.SetAmountDescription)


@subrouter.message(AddProject.SetAmountDescription)
async def check_new_project(mess: Message, state: FSMContext, bot: Bot):
    try:
        del_kb = (await state.get_data())["del"]
        await bot.edit_message_reply_markup(mess.chat.id, del_kb, reply_markup=None)
    except (KeyError, TelegramBadRequest):
        pass
    await state.update_data({"amount_des": mess.html_text})
    data = await state.get_data()
    if data['photo_id'] is not None:
        file_info = await bot.get_file(data['photo_id'])
        destination = f'{home}/photo/{data["photo_id"]}.jpg'
        await bot.download_file(file_info.file_path, destination)
        photo = FSInputFile(destination)
        msg = await mess.answer_photo(photo=photo, caption=f"{data['name']}\n{data['description']}")
        await mess.answer(data['amount_des'], reply_markup=kbi_a.confirmation())
        await state.update_data({"text": mess.html_text, "photo_id": msg.photo[-1].file_id, "del": msg.message_id})
        if os.path.exists(destination):
            os.rename(destination, f"{home}/photo/{msg.photo[-1].file_id}.jpg")
    else:
        await mess.answer(f"{data['name']}\n{data['description']}")
        await mess.answer(data['amount_des'], reply_markup=kbi_a.confirmation())
        await state.update_data({"text": mess.html_text, "photo_id": None})
    await state.set_state(AddProject.CheckProject)


@subrouter.callback_query(F.data == "yes", AddProject.CheckProject)
async def save_new_project(call: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    try:
        await bot.edit_message_reply_markup(call.from_user.id, data['del'], reply_markup=None)
    except (KeyError, TelegramBadRequest):
        pass
    database.save_new_service(data)
    await state.clear()
    await call.message.answer("Проект сохранен!", reply_markup=kbi_a.admin_menu(call.from_user.id))
    await call.message.delete()


# #################################################################################################################### #
# ############################################# УДАЛЕНИЕ УСЛУГ ####################################################### #
# #################################################################################################################### #
@subrouter.callback_query(F.data.split("_")[0] == "delserv", StateFilter(None))
async def check_del_service(call: CallbackQuery):
    await call.message.edit_reply_markup(
        reply_markup=kbi_a.confirmation(txt_y="Удалить", txt_n="Отмена",
                                        cd_y=f"yesdelserv_{call.data.split('_')[-1]}",
                                        cd_n=f"service_{call.data.split('_')[-1]}",
                                        canc_data="start"))


@subrouter.callback_query(F.data.split("_")[0] == "yesdelserv", StateFilter(None))
async def del_service(call: CallbackQuery):
    database.deleted_service(int(call.data.split("_")[-1]))
    await call.message.edit_text("Сервис удален!", reply_markup=kbi.menu_services())
