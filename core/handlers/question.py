from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.filters.state import State, StatesGroup, StateFilter

from core.settings import get_chat_id
from core.keyboard import inline as kbi

subrouter = Router()


class Question(StatesGroup):
    Mess = State()
    CheckMessage = State()


@subrouter.callback_query(F.data == "question", StateFilter(None))
@subrouter.callback_query(F.data == "no", Question.CheckMessage)
async def set_name_form(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    msg = await call.message.answer("Вы можете связаться с нами через указанные контакты. "
                                    "Или напишите свое обращение, я передам его менеджеру",
                                    reply_markup=kbi.question_btn())
    await state.update_data({"del": msg.message_id})
    await state.set_state(Question.Mess)
    return


@subrouter.message(Question.Mess)
async def set_phone_form(mess: Message, state: FSMContext, bot: Bot):
    try:
        msg_del = (await state.get_data())["del"]
        await bot.edit_message_reply_markup(mess.from_user.id, msg_del, reply_markup=None)
    except: pass
    await state.set_data({"text": mess.md_text})
    await mess.answer("Проверьте своё обращение:\n\n"
                      f"{mess.html_text}\n\n"
                      f"Если все верно, я отправлю обращение",
                      reply_markup=kbi.check_up())
    await state.set_state(Question.CheckMessage)
    return


@subrouter.callback_query(Question.CheckMessage, F.data == "yes")
async def send_nil(call: CallbackQuery, state: FSMContext, bot: Bot):
    await call.message.edit_text("Спасибо за информацию, наш менеджер с вами свяжется!", reply_markup=kbi.to_return())
    data = await state.get_data()
    await bot.send_message(get_chat_id(),
                           f"Обращение из бота!\n"
                           f"Текст обращения: {data['text']}\n"
                           f"Имя: [{call.from_user.first_name}](tg://user?id={call.from_user.id})\n"
                           f"Ссылка: @{call.from_user.username}\n\n", parse_mode="Markdown")
    await state.clear()
    return
