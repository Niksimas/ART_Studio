from aiogram import Router, F

from .basic import router as adm
from .cancel_state import subrouter as cst
from .add_del_service import subrouter as add_serv
from .edit_service import subrouter as edit_poj
from .edit_message import subrouter as edit_mess
from core.filters.filters import IsAdminMess

router_admin = Router()
router_admin.include_routers(adm, edit_poj, add_serv, edit_mess)
# Должен быть последним
router_admin.include_router(cst)

router_admin.message.filter(IsAdminMess())
router_admin.callback_query.filter(IsAdminMess())
