from typing import Final


class Texts:
    class Messages:
        admin_start: Final[str] = (
            "Панель администратора\n"
            "Доступные команды:\n"
            "/add_admin - добавить администратора\n"
            "/remove_admin - удалить администратора\n"
            "/list_admins - список администраторов"
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
            "Подтвердите удаление администратора: "
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
    
    class Buttons:
        remove_admin_confirm: Final[str] = "Подтвердить удаление"
        remove_admin_cancel: Final[str] = "Отмена"
