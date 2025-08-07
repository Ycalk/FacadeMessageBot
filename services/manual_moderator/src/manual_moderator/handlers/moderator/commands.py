from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from manual_moderator.utils import Moderator, Texts, BotData

moderator_commands_router = Router()


@moderator_commands_router.message(Command("start_moderation"))
async def cmd_start_moderation(message: Message, state: FSMContext):
    if not message.from_user:
        return
    moderator = await Moderator.get_or_none(telegram_id=message.from_user.id)
    if not moderator:
        return
    await state.clear()

    if moderator.is_active:
        await message.answer(Texts.Messages.start_moderation_already_active)
    else:
        moderator.is_active = True
        await moderator.save()
        await message.answer(Texts.Messages.start_moderation_success)


@moderator_commands_router.message(Command("stop_moderation"))
async def cmd_stop_moderation(message: Message, state: FSMContext):
    if not message.from_user:
        return
    moderator = await Moderator.get_or_none(telegram_id=message.from_user.id)
    if not moderator:
        return
    await state.clear()

    if not moderator.is_active:
        await message.answer(Texts.Messages.stop_moderation_already_inactive)
    else:
        moderator.is_active = False
        await moderator.save()
        if moderator.processing_message:
            await BotData.add_message_to_processing_queue(moderator.processing_message)
        moderator.processing_message = None
        await message.answer(Texts.Messages.stop_moderation_success)
