from aiogram import Router, F

from .basic import router as adm
from .cancel_state import subrouter as cst
from .add_service import subrouter as add_serv
from .edit_service import subrouter as edit_poj
from .edit_message import subrouter as edit_mess
from core.database.database import get_all_id_admin

router_admin = Router()
router_admin.include_routers(adm, edit_poj, add_serv, edit_mess)
# Должен быть последним
router_admin.include_router(cst)

router_admin.message.filter(F.from_user.id.in_(get_all_id_admin()))
router_admin.callback_query.filter(F.from_user.id.in_(get_all_id_admin()))
