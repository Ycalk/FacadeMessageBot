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
from manual_moderator.utils import Admin, Texts, Config
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
                        text=Texts.Buttons.remove_admin_confirm,
                        callback_data=f"confirm:{removing_admin.telegram_id}",
                    ),
                    InlineKeyboardButton(
                        text=Texts.Buttons.remove_admin_cancel,
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
