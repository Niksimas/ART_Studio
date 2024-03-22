from aiogram import Router

from .basic import router as gen
from .services import router as proj
from .question import subrouter as form
from .recording import subrouter as record

main_router = Router()

main_router.include_routers(gen, proj, form, record)
