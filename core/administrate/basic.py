from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter, Command
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message

from core.database import database
from core.keyboard import inline_admin as kbi
from core.settings import settings, home, set_chat_id
from core.google.sheets import load_user

router = Router()

bot = Bot(token=settings.bots.bot_token, parse_mode='HTML')


@router.callback_query(F.data == "admin")
@router.callback_query(F.data == "no", StateFilter(None))
async def menu_admins_call(call: CallbackQuery, state: FSMContext):
    try:
        await call.message.edit_text("Доступные процессы: ", reply_markup=kbi.admin_menu(call.from_user.id))
    except TelegramBadRequest:
        await call.message.answer("Доступные процессы: ", reply_markup=kbi.admin_menu(call.from_user.id))
        await call.message.delete()
    await state.clear()


@router.callback_query(F.data == "new_chat", StateFilter(None))
async def manual_new_chat_admin(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Для того чтобы сменить или настроить чат для администраторов, необходимо:\n"
                                 "1. Создать чат\n"
                                 "2. Включить, а затем выключить в новом чате темы\n"
                                 "3. Добавить туда вашего бота\n"
                                 "4. Выдать боту права администратора\n"
                                 "5. Скопировать и отправить команду в новый чат /new_chat_admins",
                                 reply_markup=kbi.custom_btn("Назад", "admin"))
    await state.clear()


@router.message(Command("new_chat_admins"), F.chat.type == "supergroup")
async def set_new_chat_admin(mess: Message):
    set_chat_id(mess.chat.id)
    await mess.answer("Новый чат установлен! Не забудьте добавить в него всех администраторов!")


@router.message(Command("new_chat_admins"), F.chat.type == "group")
async def set_new_chat_admin(mess: Message):
    await mess.answer("Данный чат не является супергруппой! Включите, а затем выключите в этом чате темы, "
                      "и повторно отправьте команду /new_chat_admins")


########################################################################################################################
# ################################ Добавление удаление администраторов ############################################### #
########################################################################################################################
@router.callback_query(F.data == "add_admin", StateFilter(None))
async def add_admin(call: CallbackQuery, bot: Bot):
    await call.message.edit_text("Отправьте новому администратору ссылку:\n"
                                 f"https://t.me/{(await bot.me()).username}?start={call.message.message_id}")
    with open(f"{home}/administrate/code.txt", "w") as f:
        f.write(str(call.message.message_id))


def check_code_admin(code_in: int) -> bool:
    with open(f"{home}/administrate/code.txt", "r+") as f:
        try:
            saved_code = int(f.read())
        except:
            return False
        f.write("a")
    return saved_code == code_in


@router.callback_query(F.data.split("_")[0] == "no", StateFilter(None))
@router.callback_query(F.data == "del_admin")
async def del_admin_menu(call: CallbackQuery):
    await call.message.edit_text("Выберите кого удаляем:", reply_markup=kbi.del_admin(database.get_all_data_admin()))


@router.callback_query(F.data.split("_")[0] == "del", StateFilter(None))
async def check_del_admin(call: CallbackQuery):
    name = database.get_user_name(int(call.data.split('_')[-1]))
    await call.message.edit_text(f"Вы уверены в удалении {name}?",
                                 reply_markup=kbi.confirmation(cd_y=f"Yes_{call.data.split('_')[-1]}"))


@router.callback_query(F.data.split("_")[0] == "yes", StateFilter(None))
async def del_admin(call: CallbackQuery):
    database.deleted_admin(int(call.data.split("_")[-1]))
    await call.message.edit_text("Администратор удален!", reply_markup=kbi.admin_menu(call.from_user.id))


########################################################################################################################
# ########################################### Пользователи ########################################################### #
########################################################################################################################
@router.callback_query(F.data == "users", StateFilter(None))
async def del_admin(call: CallbackQuery):
    await call.message.edit_text("Ожидайте загрузки данных!")
    load_user()
    await call.message.edit_text("Данные о пользователях загружены в таблицу:\n"
                                 f"{settings.link_sheet}",
                                 reply_markup=kbi.cancel_admin("admin"))
