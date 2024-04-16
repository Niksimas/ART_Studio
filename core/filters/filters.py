from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from core.database.database import get_all_id_admin


class IsAdminMess(BaseFilter):
    async def __call__(self, mess: Message = None, call: CallbackQuery = None):
        if call is None:
            return mess.from_user.id in get_all_id_admin()
        else:
            return call.from_user.id in get_all_id_admin()

