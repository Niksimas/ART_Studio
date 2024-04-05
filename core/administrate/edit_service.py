import os

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, FSInputFile, InputMediaPhoto

from core.settings import home
from core.database import database
from core.keyboard import inline_admin as kbi_a
from core.handlers import basic as hand_base


subrouter = Router()


# #################################################################################################################### #
# ####################################### ВЫБОР ПОЛЯ РЕДАКТИРОВАНИЯ ################################################## #
# #################################################################################################################### #
class EditService(StatesGroup):
    ChoiceAmount = State()
    CheckText = State()
    CheckName = State()
    CheckPhoto = State()
    CheckAmount = State()
    SetText = State()
    SetName = State()
    SetPhoto = State()
    SetAmount = State()
    SetNameAmount = State()


@subrouter.callback_query(F.data.startswith("edit_service_"))
async def check_data_btn(call: CallbackQuery):
    data_mess = database.get_service(int(call.data.split("_")[-1]))
    try:
        await call.message.edit_text(f"{data_mess['description']}",
                                     reply_markup=kbi_a.edit_service(call.data.split("_")[-1]))
    except TelegramBadRequest:
        await call.message.edit_media(InputMediaPhoto(media=data_mess["photo_id"],
                                                      caption=data_mess['description']),
                                      reply_markup=kbi_a.edit_service(call.data.split("_")[-1]))


# #################################################################################################################### #
# ####################################### Редактирование текста ###################################################### #
# #################################################################################################################### #
@subrouter.callback_query(F.data.startswith("edit_s_text_"))
@subrouter.callback_query(F.data == "no", EditService.CheckText)
async def set_new_data_btn(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if call.data == "no":
        calld = data['type_service']
    else:
        calld = call.data.split("_")[-1]
    try:
        msg = await call.message.edit_text(f"Отправьте новый текст сообщения \n\n",
                                           reply_markup=kbi_a.cancel_admin(f"service_{calld}"))
    except TelegramBadRequest:
        msg = await call.message.answer(f"Отправьте новый текст сообщения \n\n",
                                        reply_markup=kbi_a.cancel_admin(f"service_{calld}"))
        await call.message.delete()
    await state.set_state(EditService.SetText)
    if call.data != "no":
        await state.update_data({"del": msg.message_id, "type_service": call.data.split("_")[-1], "type_edit": "description"})
    else:
        await state.update_data({"del": msg.message_id})


@subrouter.message(EditService.SetText)
async def set_new_data_btn(mess: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    try:
        await bot.edit_message_reply_markup(mess.chat.id, data['del'], reply_markup=None)
    except (KeyError, TelegramBadRequest):
        pass
    data_mess = database.get_service(data['type_service'])
    if len(mess.text) > (4095 - len(data_mess['name'])) and data_mess['photo_id'] is None:
        msg = await mess.answer(f"Длинна нового текста превышает допустимый предел! Удалите {len(mess.text)-4096}")
        await state.update_data({"del": msg.message_id})
        return
    elif len(mess.text) > (1023 - len(data_mess['name'])) and data_mess['photo_id'] is not None:
        msg = await mess.answer(f"Длинна нового текста превышает допустимый предел! Удалите {len(mess.text) - 1024}")
        await state.update_data({"del": msg.message_id})
        return
    data_mess[data['type_edit']] = mess.html_text
    await state.update_data(data_mess)
    await mess.answer(f"{data_mess['description']}",
                      reply_markup=kbi_a.confirmation(txt_y="Сохранить", txt_n="Заново",
                                                      canc_data=f"service_{data['type_service']}"))
    await state.set_state(EditService.CheckText)


# #################################################################################################################### #
# ####################################### РЕДАКТИРОВАНИЕ ФОТОГРАФИИ ################################################## #
# #################################################################################################################### #
@subrouter.callback_query(F.data.startswith("edit_s_photo_"))
@subrouter.callback_query(F.data == "no", EditService.CheckPhoto)
async def set_new_data_btn(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if call.data == "no":
        calld = data['type_service']
    else:
        calld = call.data.split("_")[-1]
    data_mess = database.get_service(int(call.data.split("_")[-1]))
    if len(data_mess['description']) > 1024:
        await call.answer(f"Невозможно установить фотографию! Сократите текст на {len(data_mess['description'])-1024} символов!")
        return
    try:
        msg = await call.message.edit_text(f"Отправьте ОДНУ новую фотографию",
                                           reply_markup=kbi_a.cancel_admin(f"service_{calld}"))
    except TelegramBadRequest:
        msg = await call.message.answer(f"Отправьте ОДНУ новую фотографию",
                                        reply_markup=kbi_a.cancel_admin(f"service_{calld}"))
        await call.message.delete()
    await state.set_state(EditService.SetPhoto)
    if call.data != "no":
        await state.update_data({"del": msg.message_id, "type_service": call.data.split("_")[-1], "type_edit": "photo_id"})
    else:
        await state.update_data({"del": msg.message_id})


@subrouter.message(F.media_group_id, EditService.SetPhoto)
async def save_photo_front(mess: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    try:
        await bot.edit_message_reply_markup(mess.chat.id, data['del'], reply_markup=None)
    except (KeyError, TelegramBadRequest):
        pass
    try:
        b = data["group_id"]
    except KeyError:
        msg = await mess.answer("Можно прикрепить только одну фотографию!",
                                reply_markup=kbi_a.cancel_admin(f"service_{data['type_service']}"))
        await state.update_data({"group_id": mess.media_group_id, "del": msg.message_id})


@subrouter.message(F.photo, EditService.SetPhoto)
async def save_photo_front(mess: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    try:
        await bot.edit_message_reply_markup(mess.chat.id, data['del'], reply_markup=None)
    except (KeyError, TelegramBadRequest):
        pass
    data_mess = database.get_service(data["type_service"])
    file_id = mess.photo[-1].file_id
    file_info = await bot.get_file(file_id)
    destination = f'{home}/photo/{file_id}.jpg'
    await bot.download_file(file_info.file_path, destination)
    photo = FSInputFile(destination)
    msg = await mess.answer_photo(photo=photo, caption=f"Сохранить?",
                                  reply_markup=kbi_a.confirmation(canc_data=f"service_{data['type_service']}"))
    if os.path.exists(destination):
        os.rename(destination, f"{home}/photo/{msg.photo[-1].file_id}.jpg")
    await state.update_data(data_mess)
    await state.update_data({"photo_id": msg.photo[-1].file_id})
    await state.set_state(EditService.CheckPhoto)


# #################################################################################################################### #
# ####################################### РЕДАКТИРОВАНИЕ НАЗВАНИЯ ################################################## #
# #################################################################################################################### #
@subrouter.callback_query(F.data.startswith("edit_s_name_"))
@subrouter.callback_query(F.data == "no", EditService.CheckName)
async def set_new_data_btn(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if call.data == "no":
        calld = data['type_service']
    else:
        calld = call.data.split("_")[-1]
    try:
        msg = await call.message.edit_text(f"Отправьте новое название",
                                           reply_markup=kbi_a.cancel_admin(f"service_{calld}"))
    except TelegramBadRequest:
        msg = await call.message.answer(f"Отправьте новое название",
                                        reply_markup=kbi_a.cancel_admin(f"service_{calld}"))
        await call.message.delete()
    await state.set_state(EditService.SetName)
    if call.data != "no":
        await state.update_data({"del": msg.message_id, "type_service": call.data.split("_")[-1], "type_edit": "name"})
    else:
        await state.update_data({"del": msg.message_id})


@subrouter.message(EditService.SetName)
async def set_new_data_btn(mess: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    try:
        await bot.edit_message_reply_markup(mess.chat.id, data['del'], reply_markup=None)
    except (KeyError, TelegramBadRequest):
        pass
    data_mess = database.get_service(data['type_service'])
    data_mess[data['type_edit']] = mess.html_text
    await state.update_data(data_mess)
    await mess.answer(f"{data_mess['name']}", reply_markup=kbi_a.confirmation())
    await state.set_state(EditService.CheckName)


# #################################################################################################################### #
# ####################################### Редактирование СТОИМОСТЕЙ ################################################## #
# #################################################################################################################### #
@subrouter.callback_query(F.data.startswith("edit_s_amount_"))
@subrouter.callback_query(F.data == "no", EditService.CheckAmount)
async def set_new_data_btn(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if call.data == "no":
        calld = data['type_service']
    else:
        calld = call.data.split("_")[-1]
    data_mess = database.get_service(int(calld))
    try:
        msg = await call.message.edit_text(f"Прайс который установлен сейчас:\n"
                                           f"{data_mess['amount_des']}\n\nОтправьте новый прайс",
                                           reply_markup=kbi_a.cancel_admin(f"service_{calld}"))
    except TelegramBadRequest:
        msg = await call.message.answer(f"Прайс который установлен сейчас:\n"
                                           f"Отправьте новый текст сообщения: \n\n{data_mess['amount_des']}",
                                        reply_markup=kbi_a.cancel_admin(f"service_{calld}"))
        await call.message.delete()
    await state.set_state(EditService.SetAmount)
    if call.data != "no":
        await state.update_data({"del": msg.message_id, "type_service": call.data.split("_")[-1], "type_edit": "amount_des"})
    else:
        await state.update_data({"del": msg.message_id})


@subrouter.message(EditService.SetAmount)
async def set_new_data_btn(mess: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    try:
        await bot.edit_message_reply_markup(mess.chat.id, data['del'], reply_markup=None)
    except (KeyError, TelegramBadRequest):
        pass
    data_mess = database.get_service(data['type_service'])
    data_mess[data['type_edit']] = mess.html_text
    await state.update_data(data_mess)
    await mess.answer(f"{data_mess[data['type_edit']]}",
                      reply_markup=kbi_a.confirmation(txt_y="Сохранить", txt_n="Заново",
                                                      canc_data=f"service_{data['type_service']}"))
    await state.set_state(EditService.CheckText)


# #################################################################################################################### #
# ####################################### СОХРАНЕНИЕ ИЗМЕНЕНИЙ ####################################################### #
# #################################################################################################################### #
@subrouter.callback_query(F.data == "yes", EditService.CheckName)
@subrouter.callback_query(F.data == "yes", EditService.CheckAmount)
@subrouter.callback_query(F.data == "yes", EditService.CheckPhoto)
@subrouter.callback_query(F.data == "yes", EditService.CheckText)
async def set_new_data_service(call: CallbackQuery, state: FSMContext):
    new_data = await state.get_data()
    database.update_service(new_data)
    await hand_base.start_call(call, state)
