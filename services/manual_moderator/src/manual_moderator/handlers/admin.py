from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    InaccessibleMessage,
)
from datetime import datetime
from manual_moderator.utils import Admin, Texts, Config, Moderator, BotData
from manual_moderator.filters import AdminState

admin_router = Router()


# region Add Admin


@admin_router.message(Command("add_admin"))
async def cmd_add_admin(message: Message, state: FSMContext):
    if not message.from_user or not (await Admin.get_or_none(message.from_user.id)):
        return
    await state.clear()

    await state.set_state(AdminState.add_admin_set_telegram_id)
    await message.answer(Texts.Messages.add_admin_set_telegram_id)


@admin_router.message(AdminState.add_admin_set_telegram_id)
async def add_admin_set_telegram_id(message: Message, state: FSMContext):
    if not message.from_user or not (await Admin.get_or_none(message.from_user.id)):
        return

    if not message.text or not message.text.isdigit():
        await message.answer(Texts.Messages.add_admin_invalid_telegram_id)
        return

    telegram_id = int(message.text)
    await Admin(telegram_id=telegram_id, first_name="New Admin").save()
    await message.answer(
        Texts.Messages.add_admin_success.format(telegram_id=telegram_id)
    )
    await state.clear()


# region Remove Admin


@admin_router.message(Command("remove_admin"))
async def cmd_remove_admin(message: Message, state: FSMContext):
    if not message.from_user or not (await Admin.get_or_none(message.from_user.id)):
        return
    await state.clear()
    await state.set_state(AdminState.remove_admin_set_telegram_id)
    await message.answer(Texts.Messages.remove_admin_set_telegram_id)


@admin_router.message(AdminState.remove_admin_set_telegram_id)
async def remove_admin_set_telegram_id(message: Message, state: FSMContext):
    if not message.from_user or not (await Admin.get_or_none(message.from_user.id)):
        return

    if (
        not message.text
        or not message.text.isdigit()
        or not await Admin.exists(telegram_id=int(message.text))
    ):
        await message.answer(
            Texts.Messages.remove_admin_not_found.format(telegram_id=message.text)
        )
        await state.clear()
        return

    telegram_id = int(message.text)
    if telegram_id == message.from_user.id:
        await message.answer(Texts.Messages.remove_admin_cannot_remove_self)
        await state.clear()
        return

    if telegram_id == Config.MAIN_ADMIN_ID:
        await message.answer(Texts.Messages.remove_admin_cannot_remove_main_admin)
        await state.clear()
        return

    removing_admin = await Admin.get(telegram_id=telegram_id)

    await message.answer(
        Texts.Messages.remove_admin_confirm.format(
            telegram_id=telegram_id,
            first_name=removing_admin.first_name or "",
            last_name=removing_admin.last_name or "",
            username=f"@{removing_admin.username}" if removing_admin.username else "",
        ),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=Texts.Buttons.remove_confirm,
                        callback_data=f"confirm:{removing_admin.telegram_id}",
                    ),
                    InlineKeyboardButton(
                        text=Texts.Buttons.remove_cancel,
                        callback_data="cancel",
                    ),
                ],
            ]
        ),
    )
    await state.set_state(AdminState.remove_admin_confirm)


@admin_router.callback_query(AdminState.remove_admin_confirm)
async def remove_admin_confirm(callback_query: CallbackQuery, state: FSMContext):
    if (
        not callback_query.from_user
        or not (await Admin.get_or_none(callback_query.from_user.id))
        or not callback_query.data
        or not callback_query.message
        or isinstance(callback_query.message, InaccessibleMessage)
    ):
        return
    if callback_query.data.startswith("confirm:"):
        telegram_id = int(callback_query.data.split(":")[1])
        await Admin.delete(telegram_id=telegram_id)
        await callback_query.message.edit_text(
            text=Texts.Messages.remove_admin_success.format(telegram_id=telegram_id),
            reply_markup=None,
        )
        await state.clear()
    elif callback_query.data == "cancel":
        await callback_query.message.edit_text(
            text=Texts.Messages.remove_admin_cancelled, reply_markup=None
        )
        await state.clear()


# region List Admins


@admin_router.message(Command("list_admins"))
async def cmd_list_admins(message: Message, state: FSMContext):
    if not message.from_user or not (await Admin.get_or_none(message.from_user.id)):
        return
    await state.clear()
    admins = await Admin.all()
    if len(admins) == 0:
        await message.answer(Texts.Messages.list_admins_no_admins)
        return

    for admin in admins:
        await message.answer(
            Texts.Messages.list_admins_admin_info.format(
                telegram_id=admin.telegram_id,
                first_name=admin.first_name or "",
                last_name=admin.last_name or "",
                username=f"@{admin.username}" if admin.username else "",
            )
        )


# region Add Moderator


@admin_router.message(Command("add_moderator"))
async def cmd_add_moderator(message: Message, state: FSMContext):
    if not message.from_user or not (await Admin.get_or_none(message.from_user.id)):
        return
    await state.clear()

    await state.set_state(AdminState.add_moderator_set_telegram_id)
    await message.answer(Texts.Messages.add_moderator_set_telegram_id)


@admin_router.message(AdminState.add_moderator_set_telegram_id)
async def add_moderator_set_telegram_id(message: Message, state: FSMContext):
    if not message.from_user or not (await Admin.get_or_none(message.from_user.id)):
        return

    if not message.text or not message.text.isdigit():
        await message.answer(Texts.Messages.add_moderator_invalid_telegram_id)
        return

    telegram_id = int(message.text)
    await Moderator(
        telegram_id=telegram_id, first_name="New Moderator", processing_message=None
    ).save()
    await message.answer(
        Texts.Messages.add_moderator_success.format(telegram_id=telegram_id)
    )
    await state.clear()


# region Remove Moderator


@admin_router.message(Command("remove_moderator"))
async def cmd_remove_moderator(message: Message, state: FSMContext):
    if not message.from_user or not (await Admin.get_or_none(message.from_user.id)):
        return
    await state.clear()
    await state.set_state(AdminState.remove_moderator_set_telegram_id)
    await message.answer(Texts.Messages.remove_moderator_set_telegram_id)


@admin_router.message(AdminState.remove_moderator_set_telegram_id)
async def remove_moderator_set_telegram_id(message: Message, state: FSMContext):
    if not message.from_user or not (await Admin.get_or_none(message.from_user.id)):
        return

    if (
        not message.text
        or not message.text.isdigit()
        or not await Moderator.exists(telegram_id=int(message.text))
    ):
        await message.answer(
            Texts.Messages.remove_moderator_not_found.format(telegram_id=message.text)
        )
        await state.clear()
        return

    removing_moderator = await Moderator.get(telegram_id=int(message.text))

    await message.answer(
        Texts.Messages.remove_moderator_confirm.format(
            telegram_id=removing_moderator.telegram_id,
            first_name=removing_moderator.first_name or "",
            last_name=removing_moderator.last_name or "",
            username=f"@{removing_moderator.username}"
            if removing_moderator.username
            else "",
            is_active="Да" if removing_moderator.is_active else "Нет",
            messages_processed=await removing_moderator.get_processed_messages_count(),
            last_activity=datetime.fromtimestamp(
                removing_moderator.last_activity
            ).strftime("%Y-%m-%d %H:%M:%S")
            if removing_moderator.last_activity
            else "",
        ),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=Texts.Buttons.remove_confirm,
                        callback_data=f"confirm:{removing_moderator.telegram_id}",
                    ),
                    InlineKeyboardButton(
                        text=Texts.Buttons.remove_cancel,
                        callback_data="cancel",
                    ),
                ],
            ]
        ),
    )
    await state.set_state(AdminState.remove_moderator_confirm)


@admin_router.callback_query(AdminState.remove_moderator_confirm)
async def remove_moderator_confirm(callback_query: CallbackQuery, state: FSMContext):
    if (
        not callback_query.from_user
        or not (await Admin.get_or_none(callback_query.from_user.id))
        or not callback_query.data
        or not callback_query.message
        or isinstance(callback_query.message, InaccessibleMessage)
    ):
        return
    if callback_query.data.startswith("confirm:"):
        telegram_id = int(callback_query.data.split(":")[1])

        removing_moderator = await Moderator.get(telegram_id=telegram_id)
        if removing_moderator.processing_message:
            await BotData.add_message_to_processing_queue(
                removing_moderator.processing_message
            )

        await Moderator.delete(telegram_id=telegram_id)
        await callback_query.message.edit_text(
            text=Texts.Messages.remove_moderator_success.format(
                telegram_id=telegram_id
            ),
            reply_markup=None,
        )
        await state.clear()
    elif callback_query.data == "cancel":
        await callback_query.message.edit_text(
            text=Texts.Messages.remove_moderator_cancelled, reply_markup=None
        )
        await state.clear()


# region List Moderators


@admin_router.message(Command("list_moderators"))
async def cmd_list_moderators(message: Message, state: FSMContext):
    if not message.from_user or not (await Admin.get_or_none(message.from_user.id)):
        return
    await state.clear()
    moderators = await Moderator.all()
    if len(moderators) == 0:
        await message.answer(Texts.Messages.list_moderators_no_moderators)
        return

    for moderator in moderators:
        await message.answer(
            Texts.Messages.list_moderators_moderator_info.format(
                telegram_id=moderator.telegram_id,
                first_name=moderator.first_name or "",
                last_name=moderator.last_name or "",
                username=f"@{moderator.username}" if moderator.username else "",
                is_active="Да" if moderator.is_active else "Нет",
                messages_processed=await moderator.get_processed_messages_count(),
                last_activity=datetime.fromtimestamp(moderator.last_activity).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                if moderator.last_activity
                else "",
            )
        )


# region Enable Auto Approve


@admin_router.message(Command("enable_auto_approve"))
async def cmd_enable_auto_approve(message: Message, state: FSMContext):
    if not message.from_user or not (await Admin.get_or_none(message.from_user.id)):
        return
    await state.clear()
    if await BotData.is_auto_approve_enabled():
        await message.answer(Texts.Messages.enable_auto_approve_already_enabled)
        return
    await BotData.enable_auto_approve()
    await message.answer(Texts.Messages.enable_auto_approve_success)


# region Disable Auto Approve


@admin_router.message(Command("disable_auto_approve"))
async def cmd_disable_auto_approve(message: Message, state: FSMContext):
    if not message.from_user or not (await Admin.get_or_none(message.from_user.id)):
        return
    await state.clear()
    if not await BotData.is_auto_approve_enabled():
        await message.answer(Texts.Messages.disable_auto_approve_already_disabled)
        return
    await BotData.disable_auto_approve()
    await message.answer(Texts.Messages.disable_auto_approve_success)


# region Bot Status


@admin_router.message(Command("bot_status"))
async def cmd_bot_status(message: Message, state: FSMContext):
    if not message.from_user or not (await Admin.get_or_none(message.from_user.id)):
        return
    await state.clear()
    await message.answer(
        Texts.Messages.bot_status.format(
            auto_approve_status="Включено"
            if await BotData.is_auto_approve_enabled()
            else "Отключено",
            admin_count=len(await Admin.all()),
            moderator_count=len(await Moderator.all()),
            processing_queue_count=await BotData.get_processing_queue_length(),
        )
    )
