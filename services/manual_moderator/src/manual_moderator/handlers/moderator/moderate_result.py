from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters.base import Filter
from manual_moderator.utils import Moderator, Texts

moderator_moderate_result_router = Router()


class ModeratorCallbackFilter(Filter):
    async def __call__(self, callback_query: CallbackQuery) -> bool:
        moderator = await Moderator.get_or_none(callback_query.from_user.id)
        return (
            moderator is not None
            and callback_query.message is not None
            and isinstance(callback_query.message, Message)
            and callback_query.data is not None
        )


@moderator_moderate_result_router.callback_query(ModeratorCallbackFilter())
async def moderate_result_callback_handler(callback_query: CallbackQuery):
    moderator = await Moderator.get_or_none(callback_query.from_user.id)
    if (
        not moderator
        or not callback_query.message
        or not isinstance(callback_query.message, Message)
        or not callback_query.data
    ):
        return
    if not moderator.processing_message:
        if moderator.is_active:
            await callback_query.answer(
                Texts.Messages.no_message_but_active,
                show_alert=True,
            )
            # Проверяем, нужно ли редактировать сообщение
            if callback_query.message.text != Texts.Messages.no_message_but_active or callback_query.message.reply_markup is not None:
                await callback_query.message.edit_text(
                    Texts.Messages.no_message_but_active,
                    reply_markup=None,
                )
        else:
            await callback_query.answer(
                Texts.Messages.no_message_and_inactive,
                show_alert=True,
            )
            # Проверяем, нужно ли редактировать сообщение
            if callback_query.message.text != Texts.Messages.no_message_and_inactive or callback_query.message.reply_markup is not None:
                await callback_query.message.edit_text(
                    Texts.Messages.no_message_and_inactive,
                    reply_markup=None,
                )
        return

    if callback_query.data.startswith("approve:") or callback_query.data.startswith(
        "reject:"
    ):
        is_approve = callback_query.data.startswith("approve:")
        action = moderator.approve_message if is_approve else moderator.reject_message
        message_id = int(callback_query.data.split(":")[1])

        if not moderator.processing_message.message_id == message_id:
            wrong_message_id_text = Texts.Messages.wrong_message_id.format(
                callback_message_id=message_id,
                current_message_id=moderator.processing_message.message_id,
            )
            await callback_query.answer(
                wrong_message_id_text,
                show_alert=True,
            )
            # Проверяем, нужно ли редактировать сообщение
            if callback_query.message.text != wrong_message_id_text:
                await callback_query.message.edit_text(
                    wrong_message_id_text,
                    reply_markup=None,
                )

        else:
            await action()
            result_text = Texts.Messages.approved if is_approve else Texts.Messages.rejected
            # Проверяем, нужно ли редактировать сообщение
            if callback_query.message.text != result_text or callback_query.message.reply_markup is not None:
                await callback_query.message.edit_text(
                    result_text,
                    reply_markup=None,
                )
