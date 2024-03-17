import os

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, FSInputFile, InputMediaPhoto

from core.settings import home
from core.database import database
from core.handlers import basic as hand_base
from core.keyboard import inline_admin as kbi


subrouter = Router()


# ############################ Изменить стартовое сообщение ############################ #
class EditStartMess(StatesGroup):
    CheckOldMess = State()
    SetMessage = State()


@subrouter.callback_query(F.data == "edit_start_mess")
async def check_start_mess(call: CallbackQuery, state: FSMContext):
    data_mess = database.get_mess('start')
    if data_mess["photo_id"] is None:
        await call.message.edit_text(f"Сейчас сообщение выглядит так:\n\n{data_mess['text']}\n\n"
                                     "Желаете изменить его?", reply_markup=kbi.confirmation())
    else:
        await call.message.answer_photo(data_mess["photo_id"], caption=data_mess["text"],
                                        reply_markup=kbi.confirmation())
        await call.message.delete()
    await state.set_state(EditStartMess.CheckOldMess)


@subrouter.callback_query(F.data == "yes", EditStartMess.CheckOldMess)
@subrouter.callback_query(F.data == "no", EditStartMess.SetMessage)
async def set_new_start_mess(call: CallbackQuery, state: FSMContext):
    try:
        msg = await call.message.edit_text(f"Отправьте новое сообщение (с фотографией и/или форматированием текста):",
                                           reply_markup=kbi.cancel_admin())
    except TelegramBadRequest:
        await call.message.delete()
        msg = await call.message.answer(f"Отправьте новое сообщение (с фотографией и/или форматированием текста):",
                                        reply_markup=kbi.cancel_admin())
    await state.update_data({"del": msg.message_id})
    await state.set_state(EditStartMess.SetMessage)


@subrouter.message(EditStartMess.SetMessage)
async def check_new_mess(mess: Message, state: FSMContext, bot: Bot):
    try:
        del_kb = (await state.get_data())["del"]
        await bot.edit_message_reply_markup(mess.chat.id, del_kb, reply_markup=None)
    except (KeyError, TelegramBadRequest):
        pass

    if mess.photo is None:
        await state.update_data({"text": mess.html_text})
        await mess.answer(f"Новое сообщение выглядит теперь так:\n\n{mess.html_text}\n\nСохраняем?",
                          reply_markup=kbi.confirmation())
    else:
        file_id = mess.photo[-1].file_id
        file_info = await bot.get_file(file_id)
        destination = f'{home}/photo/{file_id}.jpg'
        await bot.download_file(file_info.file_path, destination)
        photo = FSInputFile(destination)
        msg1 = await mess.answer("Новое сообщение выглядит теперь так:")
        msg = await mess.answer_photo(photo=photo,
                                      caption=f"{mess.html_text}\n\nСохраняем?",
                                      reply_markup=kbi.confirmation())
        if os.path.exists(destination):
            os.rename(destination, f"{home}/photo/{msg.photo[-1].file_id}.jpg")
        await state.update_data({"text": mess.html_text, "photo_id": msg.photo[-1].file_id, "del": msg1.message_id})


@subrouter.callback_query(F.data == "yes", EditStartMess.SetMessage)
async def save_new_start_mess(call: CallbackQuery, state: FSMContext, bot: Bot):
    try:
        del_mess = (await state.get_data())["del"]
        await bot.delete_message(call.from_user.id, del_mess)
    except (KeyError, TelegramBadRequest):
        pass
    await call.message.delete()
    data_old = database.get_mess("start")
    if os.path.exists(f"{home}/photo/{data_old['photo_id']}.jpg"):
        os.remove(f"{home}/photo/{data_old['photo_id']}.jpg")
    data = await state.get_data()
    try:
        database.set_mess("start", data["text"], data["photo_id"])
    except KeyError:
        database.set_mess("start", data["text"])
    await call.message.answer("Новое сообщение сохранено!", reply_markup=kbi.admin_menu(call.from_user.id))
    await state.clear()


# #################################################################################################################### #
# ####################################### ВЫБОР ПОЛЯ РЕДАКТИРОВАНИЯ ################################################## #
# #################################################################################################################### #
class EditMess(StatesGroup):
    CheckText = State()
    CheckTextBtn = State()
    CheckPhoto = State()
    CheckLink = State()
    SetText = State()
    SetTextBtn = State()
    SetPhoto = State()
    SetLink = State()


@subrouter.callback_query(F.data == "edit_address")
@subrouter.callback_query(F.data == "edit_description")
async def check_data_btn(call: CallbackQuery):
    data_mess = database.get_mess(call.data.split("_")[-1])
    try:
        await call.message.edit_text(f"{data_mess['text']}\n\nВыберите что редактируем:",
                                     reply_markup=kbi.edit_btn_with_photo(call.data.split("_")[-1]))
    except TelegramBadRequest:
        await call.message.edit_media(InputMediaPhoto(media=data_mess["photo_id"],
                                                      caption=f"{data_mess['text']}\n\nВыберите что редактируем:"),
                                      reply_markup=kbi.edit_btn_with_photo(call.data.split("_")[-1]))


@subrouter.callback_query(F.data == "edit_bonuses")
@subrouter.callback_query(F.data == "edit_working_hours")
async def check_data_btn(call: CallbackQuery):
    data_mess = database.get_mess(call.data.split("_")[-1])
    await call.message.edit_text(f"{data_mess['text']}\n\nВыберите что редактируем:",
                                 reply_markup=kbi.edit_btn_with_text(call.data.split("_")[-1]))


@subrouter.callback_query(F.data == "edit_contact")
async def check_data_btn(call: CallbackQuery):
    data_mess = database.get_mess("contact")
    data_btn = database.get_mess("watsapp")
    await call.message.edit_text(f"{data_mess['text']}\n\n"
                                 f"Текст кнопки: {data_btn['text']}\n"
                                 f"Ссылка кнопки: {data_btn['link']}\n\n"
                                 f"Выберите что редактируем:",
                                 reply_markup=kbi.edit_btn_for_contact())


@subrouter.callback_query(F.data == "edit_social_network")
async def check_data_btn(call: CallbackQuery):
    data_btn1 = database.get_mess("site")
    data_btn2 = database.get_mess("tg")
    data_btn3 = database.get_mess("vk")
    data_btn4 = database.get_mess("inst")
    await call.message.edit_text(f"Первая кнопка:\n"
                                 f"--Текст: {data_btn1['text']}\n"
                                 f"--Ссылка: {data_btn1['link']}\n\n"
                                 f"Вторая кнопка:\n"
                                 f"--Текст: {data_btn2['text']}\n"
                                 f"--Ссылка: {data_btn2['link']}\n\n"
                                 f"Третья кнопка:\n"
                                 f"--Текст: {data_btn3['text']}\n"
                                 f"--Ссылка: {data_btn3['link']}\n\n"
                                 f"Четвертая кнопка:\n"
                                 f"--Текст: {data_btn4['text']}\n"
                                 f"--Ссылка: {data_btn4['link']}\n\n"
                                 f"Выберите что редактируем:",
                                 reply_markup=kbi.edit_btn_for_social_network("site", "tg", "vk", "inst"))


# #################################################################################################################### #
# ####################################### Редактирование текста ###################################################### #
# #################################################################################################################### #
@subrouter.callback_query(F.data.startswith("edit_text_"))
@subrouter.callback_query(F.data == "no", EditMess.CheckText)
async def set_new_data_btn(call: CallbackQuery, state: FSMContext):
    try:
        msg = await call.message.edit_text(f"Отправьте новый текст сообщения", reply_markup=kbi.cancel_admin())
    except TelegramBadRequest:
        msg = await call.message.answer(f"Отправьте новый текст сообщения", reply_markup=kbi.cancel_admin())
        await call.message.delete()
    await state.set_state(EditMess.SetText)
    await state.update_data({"del": msg.message_id, "type_mess": call.data.split("_")[-1], "type_edit": "text"})


@subrouter.message(EditMess.SetText)
async def set_new_data_btn(mess: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    try:
        await bot.edit_message_reply_markup(mess.chat.id, data['del'], reply_markup=None)
    except (KeyError, TelegramBadRequest):
        pass
    data_mess = database.get_mess(data['type_mess'])
    data_mess[data['type_edit']] = mess.html_text
    await state.update_data(data_mess)
    await mess.answer(f"{data_mess['text']}\n\nВерно?", reply_markup=kbi.confirmation())
    await state.set_state(EditMess.CheckText)


# #################################################################################################################### #
# ####################################### РЕДАКТИРОВАНИЕ ФОТОГРАФИИ ################################################## #
# #################################################################################################################### #
@subrouter.callback_query(F.data.startswith("edit_photo_"))
@subrouter.callback_query(F.data == "no", EditMess.CheckPhoto)
async def set_new_data_btn(call: CallbackQuery, state: FSMContext):
    try:
        msg = await call.message.edit_text(f"Отправьте ОДНУ новую фотографию", reply_markup=kbi.cancel_admin())
    except TelegramBadRequest:
        msg = await call.message.answer(f"Отправьте ОДНУ новую фотографию", reply_markup=kbi.cancel_admin())
        await call.message.delete()
    await state.set_state(EditMess.SetPhoto)
    await state.update_data({"del": msg.message_id, "type_mess": call.data.split("_")[-1], "type_edit": "photo_id"})


@subrouter.message(F.media_group_id, EditMess.SetPhoto)
async def save_photo_front(mess: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    try:
        await bot.edit_message_reply_markup(mess.chat.id, data['del'], reply_markup=None)
    except (KeyError, TelegramBadRequest):
        pass
    try:
        b = data["group_id"]
    except KeyError:
        msg = await mess.answer("Можно прикрепить только одну фотографию!", reply_markup=kbi.cancel_admin())
        await state.update_data({"group_id": mess.media_group_id, "del": msg.message_id})


@subrouter.message(F.photo, EditMess.SetPhoto)
async def save_photo_front(mess: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    data_mess = database.get_mess(data["type_mess"])
    file_id = mess.photo[-1].file_id
    file_info = await bot.get_file(file_id)
    destination = f'{home}/photo/{file_id}.jpg'
    await bot.download_file(file_info.file_path, destination)
    photo = FSInputFile(destination)
    msg = await mess.answer_photo(photo=photo,
                                  caption=f"{data_mess['text']}\n\nНовое сообщение выглядит теперь так. Сохраняем?",
                                  reply_markup=kbi.confirmation())
    if os.path.exists(destination):
        os.rename(destination, f"{home}/photo/{msg.photo[-1].file_id}.jpg")
    await state.update_data(data_mess)
    await state.update_data({"photo_id": msg.photo[-1].file_id})
    await state.set_state(EditMess.CheckPhoto)


# #################################################################################################################### #
# ####################################### Редактирование текста для кнопки ########################################### #
# #################################################################################################################### #
@subrouter.callback_query(F.data.startswith("edit_btn_text_"))
@subrouter.callback_query(F.data == "no", EditMess.CheckTextBtn)
async def set_new_data_btn(call: CallbackQuery, state: FSMContext):
    try:
        msg = await call.message.edit_text(f"Отправьте новый текст для кнопки", reply_markup=kbi.cancel_admin())
    except TelegramBadRequest:
        msg = await call.message.answer(f"Отправьте новый текст для кнопки", reply_markup=kbi.cancel_admin())
        await call.message.delete()
    await state.set_state(EditMess.SetTextBtn)
    await state.update_data({"del": msg.message_id, "type_mess": call.data.split("_")[-1], "type_edit": "text"})


@subrouter.message(EditMess.SetTextBtn)
async def set_new_data_btn(mess: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    try:
        await bot.edit_message_reply_markup(mess.chat.id, data['del'], reply_markup=None)
    except (KeyError, TelegramBadRequest):
        pass
    data_mess = database.get_mess(data['type_mess'])
    data_mess[data['type_edit']] = mess.html_text
    await state.update_data(data_mess)
    await mess.answer(f"{data_mess['text']}\n\nВерно?", reply_markup=kbi.confirmation())
    await state.set_state(EditMess.CheckTextBtn)


# #################################################################################################################### #
# ####################################### Редактирование ссылки для кнопки ########################################### #
# #################################################################################################################### #
@subrouter.callback_query(F.data.startswith("edit_btn_link_"))
@subrouter.callback_query(F.data == "no", EditMess.CheckLink)
async def set_new_data_btn(call: CallbackQuery, state: FSMContext):
    try:
        msg = await call.message.edit_text(f"Отправьте новую ссылку для кнопки", reply_markup=kbi.cancel_admin())
    except TelegramBadRequest:
        msg = await call.message.answer(f"Отправьте новую ссылку для кнопки", reply_markup=kbi.cancel_admin())
        await call.message.delete()
    await state.set_state(EditMess.SetLink)
    await state.update_data({"del": msg.message_id, "type_mess": call.data.split("_")[-1], "type_edit": "link"})


@subrouter.message(EditMess.SetLink)
async def set_new_data_btn(mess: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    try:
        await bot.edit_message_reply_markup(mess.chat.id, data['del'], reply_markup=None)
    except (KeyError, TelegramBadRequest):
        pass
    data_mess = database.get_mess(data['type_mess'])
    data_mess[data['type_edit']] = mess.html_text
    await state.update_data(data_mess)
    await mess.answer(f"{data_mess['link']}\n\nВерно?", reply_markup=kbi.confirmation())
    await state.set_state(EditMess.CheckLink)


# #################################################################################################################### #
# ####################################### СОХРАНЕНИЕ ИЗМЕНЕНИЙ ####################################################### #
# #################################################################################################################### #
@subrouter.callback_query(F.data == "yes", EditMess.CheckPhoto)
@subrouter.callback_query(F.data == "yes", EditMess.CheckTextBtn)
@subrouter.callback_query(F.data == "yes", EditMess.CheckText)
@subrouter.callback_query(F.data == "yes", EditMess.CheckLink)
async def set_new_data_btn(call: CallbackQuery, state: FSMContext):
    new_data = await state.get_data()
    database.update_message(new_data)
    await hand_base.start_call(call, state)