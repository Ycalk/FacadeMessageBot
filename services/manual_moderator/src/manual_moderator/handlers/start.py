from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from manual_moderator.utils import Admin, Texts

start_router = Router()


@start_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    if not message.from_user:
        return
    await state.clear()
    if await Admin.get_or_none(message.from_user.id):
        await message.answer(Texts.Messages.admin_start)
