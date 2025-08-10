from typing import Final


class Texts:
    class Messages:
        admin_start: Final[str] = (
            "Панель администратора\n\n"
            "Доступные команды:\n"
            "/add_admin - добавить администратора\n"
            "/remove_admin - удалить администратора\n"
            "/list_admins - список администраторов\n\n"
            "/add_moderator - добавить модератора\n"
            "/remove_moderator - удалить модератора\n"
            "/list_moderators - список модераторов\n\n"
            "/enable_auto_approve - включить автоматическое одобрение сообщений\n"
            "/disable_auto_approve - отключить автоматическое одобрение сообщений\n"
            "/bot_status - статус бота"
        )
        moderator_start: Final[str] = (
            "Панель модератора\n\n"
            "Доступные команды:\n"
            "/stop_moderation - остановить модерацию. Вы будете отмечены как неактивный модератор.\n"
            "/start_moderation - начать модерацию. Вы будете отмечены как активный модератор."
        )

        # add admin
        add_admin_set_telegram_id: Final[str] = (
            "Введите Telegram ID администратора, которого вы хотите добавить."
        )
        add_admin_success: Final[str] = "Администратор {telegram_id} успешно добавлен."
        add_admin_invalid_telegram_id: Final[str] = (
            "Некорректный Telegram ID. Пожалуйста, введите числовой ID."
        )

        # remove admin
        remove_admin_set_telegram_id: Final[str] = (
            "Введите Telegram ID администратора, которого вы хотите удалить."
        )
        remove_admin_confirm: Final[str] = (
            "Подтвердите удаление администратора:\n"
            "Telegram ID: {telegram_id}\n"
            "Имя: {first_name} {last_name}\n"
            "Username: {username}"
        )
        remove_admin_success: Final[str] = "Администратор {telegram_id} успешно удален."
        remove_admin_cancelled: Final[str] = "Удаление администратора отменено."
        remove_admin_not_found: Final[str] = (
            "Администратор с Telegram ID {telegram_id} не найден."
        )
        remove_admin_cannot_remove_self: Final[str] = (
            "Вы не можете удалить себя из списка администраторов."
        )
        remove_admin_cannot_remove_main_admin: Final[str] = (
            "Вы не можете удалить главного администратора."
        )

        # list admins
        list_admins_no_admins: Final[str] = "Нет администраторов в системе."
        list_admins_admin_info: Final[str] = (
            "Telegram ID: {telegram_id}\nИмя: {first_name} {last_name}\nUsername: {username}\n"
        )

        # add moderator
        add_moderator_set_telegram_id: Final[str] = (
            "Введите Telegram ID модератора, которого вы хотите добавить."
        )
        add_moderator_success: Final[str] = "Модератор {telegram_id} успешно добавлен."
        add_moderator_invalid_telegram_id: Final[str] = (
            "Некорректный Telegram ID. Пожалуйста, введите числовой ID."
        )

        # remove moderator
        remove_moderator_set_telegram_id: Final[str] = (
            "Введите Telegram ID модератора, которого вы хотите удалить."
        )
        remove_moderator_confirm: Final[str] = (
            "Подтвердите удаление модератора:\n"
            "Telegram ID: {telegram_id}\n"
            "Имя: {first_name} {last_name}\n"
            "Username: {username}\n"
            "Активен: {is_active}\n"
            "Сообщений обработано: {messages_processed}\n"
            "Последняя активность: {last_activity}\n\n"
            "<i>При удаление модератора, в том числе удаляется информация о обработанных им сообщений.</i>"
        )
        remove_moderator_success: Final[str] = "Модератор {telegram_id} успешно удален."
        remove_moderator_cancelled: Final[str] = "Удаление модератора отменено."
        remove_moderator_not_found: Final[str] = (
            "Модератор с Telegram ID {telegram_id} не найден."
        )

        # list moderators
        list_moderators_no_moderators: Final[str] = "Нет модераторов в системе."
        list_moderators_moderator_info: Final[str] = (
            "Telegram ID: {telegram_id}\n"
            "Имя: {first_name} {last_name}\n"
            "Username: {username}\n"
            "Активен: {is_active}\n"
            "Сообщений обработано: {messages_processed}\n"
            "Последняя активность: {last_activity}"
        )

        # enable auto approve
        enable_auto_approve_success: Final[str] = (
            "Автоматическое одобрение сообщений успешно включено."
        )
        enable_auto_approve_already_enabled: Final[str] = (
            "Автоматическое одобрение сообщений уже включено."
        )

        # disable auto approve
        disable_auto_approve_success: Final[str] = (
            "Автоматическое одобрение сообщений успешно отключено."
        )
        disable_auto_approve_already_disabled: Final[str] = (
            "Автоматическое одобрение сообщений уже отключено."
        )

        # bot status
        bot_status: Final[str] = (
            "Статус бота:\n"
            "Автоматическое одобрение сообщений: {auto_approve_status}\n"
            "Количество администраторов: {admin_count}\n"
            "Количество модераторов: {moderator_count}\n"
            "Количество сообщений в очереди на обработку: {processing_queue_count}"
        )

        # start moderation
        start_moderation_success: Final[str] = (
            "Вы успешно начали модерацию. Теперь вы отмечены как активный модератор."
        )
        start_moderation_already_active: Final[str] = (
            "Вы уже находитесь в режиме активного модератора."
        )

        # stop moderation
        stop_moderation_success: Final[str] = (
            "Вы успешно остановили модерацию.\n"
            "Теперь вы отмечены как неактивный модератор и не будете получать новые сообщения для обработки."
        )
        stop_moderation_already_inactive: Final[str] = (
            "Вы уже находитесь в режиме неактивного модератора."
        )

        # no moderators available
        no_moderators_available: Final[str] = (
            "Нет доступных модераторов для обработки сообщений.\n"
            "Сообщения будут одобрены автоматически и отправлены дальше.\n"
            "Пожалуйста, добавьте модераторов в систему или активируйте автоматическое одобрение сообщений."
        )

        # moderate result
        no_message_but_active: Final[str] = (
            "Вы находитесь в режиме активного модератора, но ваше текущее обрабатываемое сообщение неизвестно.\n"
            "Пожалуйста, свяжитесь с администратором для получения помощи."
        )
        no_message_and_inactive: Final[str] = (
            "Вы отметили себя как неактивный модератор, ваше сообщение, было обратно отправлено в очередь на обработку."
        )
        wrong_message_id: Final[str] = (
            "Вы пытаетесь обработать сообщение с ID {callback_message_id}, но оно не соответствует текущему обрабатываемому сообщению {current_message_id}.\n"
            "Пожалуйста, свяжитесь с администратором для получения помощи."
        )
        approved: Final[str] = (
            "Сообщение успешно одобрено и отправлено дальше.\n"
            "Вы можете продолжить обработку следующего сообщения."
        )
        rejected: Final[str] = (
            "Сообщение успешно отклонено.\n"
            "Вы можете продолжить обработку следующего сообщения."
        )
        marked_as_inactive: Final[str] = (
            "Вы были отмечены как неактивный модератор.\n"
            "Ваше текущее обрабатываемое сообщение было обратно отправлено в очередь на обработку.\n"
            "Чтобы снова начать модерацию, используйте команду /start_moderation."
        )
        new_message_for_moderation: Final[str] = (
            "Текст:\n\n{text}\nИмя:{name}\nГород:{city}"
        )

    class Buttons:
        remove_confirm: Final[str] = "Подтвердить удаление"
        remove_cancel: Final[str] = "Отмена"
