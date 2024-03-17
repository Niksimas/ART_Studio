import os

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart, StateFilter

from core.keyboard import inline as kb
import core.database.database as database
from core.administrate.basic import check_code_admin
from core.settings import home

router = Router()


@router.message(CommandStart(), StateFilter(None))
async def start_mess(message: Message, state: FSMContext):
    await state.clear()
    try:
        if check_code_admin(int(message.text.split(" ")[-1])):
            await message.answer("Поздравляю, вы стали администратором!")
            database.save_new_admin(message.from_user.id, message.from_user.username, message.from_user.first_name)
            return
    except:
        pass
    data_mess = database.get_mess("start")
    if data_mess["photo_id"] is None:
        await message.answer(data_mess["text"], reply_markup=kb.start(message.from_user.id))
    else:
        try:
            await message.answer_photo(data_mess["photo_id"], caption=data_mess["text"],
                                       reply_markup=kb.start(message.from_user.id))
        except TelegramBadRequest:
            destination = f'{home}/photo/{data_mess["photo_id"]}.jpg'
            msg = await message.answer_photo(photo=FSInputFile(destination), caption=data_mess['text'],
                                             reply_markup=kb.start(message.from_user.id))
            if os.path.exists(destination):
                os.rename(destination, f"{home}/photo/{msg.photo[-1].file_id}.jpg")
            database.update_photo_id("start", msg.photo[-1].file_id)
    database.save_new_user(message.from_user.id, message.from_user.username)


@router.callback_query(F.data == "start")
async def start_call(call: CallbackQuery, state: FSMContext):
    await state.clear()
    if call.data != "start":
        data_mess = database.get_mess("start")
    else:
        data_mess = database.get_mess(call.data)
    if data_mess["photo_id"] is None:
        await call.message.answer(data_mess["text"], reply_markup=kb.start(call.from_user.id))
    else:
        try:
            await call.message.answer_photo(data_mess["photo_id"], caption=data_mess["text"],
                                            reply_markup=kb.start(call.message.from_user.id))
        except TelegramBadRequest:
            destination = f'{home}/photo/{data_mess["photo_id"]}.jpg'
            msg = await call.message.answer_photo(photo=FSInputFile(destination), caption=data_mess['text'],
                                                  reply_markup=kb.start(call.message.from_user.id))
            if os.path.exists(destination):
                os.rename(destination, f"{home}/photo/{msg.photo[-1].file_id}.jpg")
            database.update_photo_id("start", msg.photo[-1].file_id)
    await call.message.delete()


@router.callback_query(F.data == "address")
@router.callback_query(F.data == "description")
@router.callback_query(F.data == "working_hours")
async def address_description_working_hours(call: CallbackQuery, state: FSMContext):
    await state.clear()
    data_mess = database.get_mess(call.data)
    try:
        await call.message.edit_text(data_mess["text"], reply_markup=kb.to_return(call.data, call.from_user.id))
    except TelegramBadRequest:
        if data_mess["photo_id"] in ["", None]:
            await call.message.answer(data_mess["text"], reply_markup=kb.to_return(call.data, call.from_user.id))
        else:
            await call.message.answer_photo(data_mess["photo_id"], caption=data_mess["text"],
                                            reply_markup=kb.to_return(call.data, call.from_user.id))
            try:
                await call.message.answer_photo(data_mess["photo_id"], caption=data_mess["text"],
                                                reply_markup=kb.to_return(call.data, call.from_user.id))
            except TelegramBadRequest:
                destination = f'{home}/photo/{data_mess["photo_id"]}.jpg'
                msg = await call.message.answer_photo(photo=FSInputFile(destination), caption=data_mess['text'],
                                                      reply_markup=kb.to_return(call.data, call.from_user.id))
                if os.path.exists(destination):
                    os.rename(destination, f"{home}/photo/{msg.photo[-1].file_id}.jpg")
                database.update_photo_id(call.data, msg.photo[-1].file_id)
        await call.message.delete()


@router.callback_query(F.data == "contacts")
async def contacts(call: CallbackQuery, bot: Bot):
    data_mess = database.get_mess("contact")
    data_btn = database.get_mess("watsapp")
    try:
        await call.message.edit_text(data_mess["text"], reply_markup=kb.url_btn(data_btn, call.from_user.id))
    except TelegramBadRequest:
        if data_mess["photo_id"] in ["", None]:
            await call.message.answer(data_mess["text"], reply_markup=kb.url_btn(data_btn, call.from_user.id))
        else:
            try:
                await call.message.answer_photo(data_mess["photo_id"], caption=data_mess["text"],
                                                reply_markup=kb.url_btn(data_btn, call.from_user.id))
            except TelegramBadRequest:
                destination = f'{home}/photo/{data_mess["photo_id"]}.jpg'
                msg = await call.message.answer_photo(photo=FSInputFile(destination), caption=data_mess['text'],
                                                      reply_markup=kb.url_btn(data_btn, call.from_user.id))
                if os.path.exists(destination):
                    os.rename(destination, f"{home}/photo/{msg.photo[-1].file_id}.jpg")
                database.update_photo_id("contact", msg.photo[-1].file_id)
        await call.message.delete()


@router.callback_query(F.data == "social_network")
async def social_network(call: CallbackQuery):
    data_mess = database.get_mess("social_network")
    data_btn_vk = database.get_mess("vk")
    data_btn_inst = database.get_mess("inst")
    data_btn_tg = database.get_mess("tg")
    data_btn_site = database.get_mess("site")
    try:
        await call.message.edit_text(data_mess["text"],
                                     reply_markup=kb.social_network_btn(data_btn_vk, data_btn_tg,
                                                                        data_btn_site, data_btn_inst, call.from_user.id))
    except TelegramBadRequest:
        await call.message.answer(data_mess["text"],
                                  reply_markup=kb.social_network_btn(data_btn_vk, data_btn_tg,
                                                                     data_btn_site, data_btn_inst, call.from_user.id))
        await call.message.delete()


@router.callback_query(F.data == "bonuses")
async def bonuses(call: CallbackQuery, state: FSMContext):
    await state.clear()
    data_mess = database.get_mess("bonuses")
    try:
        await call.message.edit_text(f"{data_mess['text']}\n\n"
                                     f"Ваш баланс: {database.get_scope_user(call.from_user.id)}",
                                     reply_markup=kb.to_return(call.data, call.from_user.id))
    except TelegramBadRequest:
        await call.message.answer(f"{data_mess['text']}\n\n"
                                  f"Ваш баланс: {database.get_scope_user(call.from_user.id)}",
                                  reply_markup=kb.to_return(call.data, call.from_user.id))
        await call.message.delete()
