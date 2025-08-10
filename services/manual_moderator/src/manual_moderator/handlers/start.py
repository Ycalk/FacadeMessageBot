from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from manual_moderator.utils import Admin, Texts, Moderator

start_router = Router()


@start_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    if not message.from_user:
        return
    await state.clear()

    admin = await Admin.get_or_none(message.from_user.id)
    moderator = await Moderator.get_or_none(message.from_user.id)

    if admin:
        if admin.first_name == "New Admin":
            await Admin(
                telegram_id=message.from_user.id,
                first_name=message.from_user.first_name,
                username=message.from_user.username,
                last_name=message.from_user.last_name,
            ).save()
        await message.answer(Texts.Messages.admin_start)

    if moderator:
        if moderator.first_name == "New Moderator":
            await Moderator(
                telegram_id=message.from_user.id,
                first_name=message.from_user.first_name,
                username=message.from_user.username,
                last_name=message.from_user.last_name,
            ).save()
        await message.answer(Texts.Messages.moderator_start)
