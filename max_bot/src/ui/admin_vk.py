"""Панель VK модерации для управления сообщениями."""

import hashlib
import secrets

from nicegui import app, ui
from sqlalchemy import select

from core.config import Config
from core.logger import get_logger
from db.models import Message, MessageStatus
from db.session import async_session
from services.stats import load_stats
from services.vk_moderator import moderate_by_vk_moderator

logger = get_logger(__name__)


def _hash_password(password: str) -> str:
    """Хеширует пароль для сравнения."""
    return hashlib.sha256(password.encode()).hexdigest()


# Статусы, которые могут быть достигнуты только через VK модерацию
_VK_VISIBLE_STATUSES = {
    MessageStatus.VK_MODERATION,
    MessageStatus.MAER_MODERATION,
    MessageStatus.APPROVED,
}


async def load_vk_messages():
    """Загружает сообщения, которые прошли (или проходят) VK модерацию."""
    async with async_session() as session:
        result = await session.execute(
            select(Message)
            .order_by(Message.created_at.desc())
        )
        rows = result.scalars().all()

        messages = []
        for msg in rows:
            meta = msg.meta or {}
            # Показываем: статусы ≥ VK или REJECTED с флагом vk_entered
            if msg.status not in _VK_VISIBLE_STATUSES:
                if not (msg.status == MessageStatus.REJECTED and meta.get("vk_entered")):
                    continue
            messages.append({
                'message': msg,
                'vk_approvals': meta.get('vk_approvals', []),
                'vk_rejections': meta.get('vk_rejections', []),
            })
        return messages


async def moderate_message_by_vk_moderator_ui(message_id: int, moderator_id: str, approve: bool):
    """Модерация сообщения VK модератором."""
    try:
        result = await moderate_by_vk_moderator(message_id, moderator_id, approve)
        logger.info(f"VK модерация {message_id} от {moderator_id}: {result}")
        return result.get("success", False), result
    except Exception as e:
        logger.error(f"Ошибка при VK модерации сообщения {message_id}: {e}")
        return False, {"error": str(e)}


@ui.page('/admin_vk', title='VK модерация')
async def vk_moderator_page():
    """Страница панели VK модерации с авторизацией."""

    # Проверяем авторизацию
    if not app.storage.user.get('auth_vk'):
        # Показываем форму входа
        with ui.card().classes('absolute-center'):
            ui.label('Вход в панель VK модерации').classes('text-h5 q-mb-md')
            password_input = ui.input(
                'Пароль', password=True, password_toggle_button=True
            ).classes('w-64')
            error_label = ui.label('').classes('text-negative')

            async def try_login():
                if not Config.ADMIN_VK_PASSWORD:
                    error_label.text = 'Пароль не настроен в конфигурации'
                    return
                if secrets.compare_digest(
                    _hash_password(password_input.value),
                    _hash_password(Config.ADMIN_VK_PASSWORD)
                ):
                    app.storage.user['auth_vk'] = True
                    ui.navigate.to('/admin_vk')
                else:
                    error_label.text = 'Неверный пароль'

            ui.button('Войти', on_click=try_login).classes('w-64')
            password_input.on('keydown.enter', try_login)
        return

    # === Авторизованная часть ===

    messages = await load_vk_messages()
    moderators = Config.vk_moderators_list
    stats = await load_stats()

    status_colors = {
        MessageStatus.INTERNAL_MODERATION: 'orange',
        MessageStatus.VK_MODERATION: 'teal',
        MessageStatus.MAER_MODERATION: 'amber',
        MessageStatus.APPROVED: 'green',
        MessageStatus.REJECTED: 'red',
    }

    status_labels = {
        MessageStatus.INTERNAL_MODERATION: 'Внутренняя',
        MessageStatus.VK_MODERATION: 'VK',
        MessageStatus.MAER_MODERATION: 'Maer',
        MessageStatus.APPROVED: 'Одобрено',
        MessageStatus.REJECTED: 'Отклонено',
    }

    def prepare_table_rows():
        """Подготавливает данные для таблицы."""
        rows = []
        for item in messages:
            msg = item['message']
            status_order = 0 if msg.status == MessageStatus.VK_MODERATION else 1
            want_photo = msg.want_photo
            shown_on_facade = msg.shown_on_facade
            photo_sent = msg.photo_sent
            rows.append({
                'id': msg.id,
                'status_order': status_order,
                'text': msg.text or '',
                'name': msg.name,
                'city': msg.city,
                'status': msg.status,
                'status_color': status_colors.get(msg.status, 'grey'),
                'created_at': msg.created_at.strftime("%Y-%m-%d %H:%M"),
                'vk_approvals': item['vk_approvals'],
                'is_moderation_active': msg.status == MessageStatus.VK_MODERATION,
                'want_photo': 'Да' if want_photo is True else ('Нет' if want_photo is False else '—'),
                'want_photo_color': 'green' if want_photo is True else ('red' if want_photo is False else 'grey'),
                'shown_on_facade': 'Да' if shown_on_facade else 'Нет',
                'shown_on_facade_color': 'deep-purple' if shown_on_facade else 'grey',
                'photo_sent': 'Да' if photo_sent else 'Нет',
                'photo_sent_color': 'green' if photo_sent else 'grey',
                'preview_url': msg.preview_url or '',
            })
        return rows

    async def refresh_table():
        """Обновляет данные таблицы и статистику."""
        nonlocal messages, stats
        messages = await load_vk_messages()
        stats = await load_stats()
        table.rows = prepare_table_rows()
        table.update()
        stats_block.refresh()
        ui.notify('Данные обновлены', type='positive')

    async def handle_vk_moderator_approve(message_id: int, moderator_id: str):
        """Обработчик одобрения от VK модератора."""
        current_msg = next((m for m in messages if m['message'].id == message_id), None)
        if not current_msg:
            return

        if moderator_id in current_msg['vk_approvals']:
            return

        success, result = await moderate_message_by_vk_moderator_ui(message_id, moderator_id, True)
        if success:
            ui.notify(f'{moderator_id} одобрил сообщение {message_id}', type='positive')
            await refresh_table()
        else:
            ui.notify(f'Ошибка: {result}', type='negative')

    async def handle_reject(message_id: int):
        """Обработчик отклонения."""
        success, result = await moderate_message_by_vk_moderator_ui(message_id, moderators[0], False)
        if success:
            ui.notify(f'Сообщение {message_id} отклонено', type='warning')
            await refresh_table()
        else:
            ui.notify(f'Ошибка: {result}', type='negative')

    async def logout():
        """Выход из панели."""
        app.storage.user['auth_vk'] = False
        ui.navigate.to('/admin_vk')

    # Заголовок с кнопкой выхода
    with ui.row().classes('w-full items-center justify-between mb-4'):
        ui.label('Панель VK модерации').classes('text-h4')
        ui.button('Выйти', on_click=logout, color='negative').props('outline size=sm')

    # Блок статистики
    @ui.refreshable
    def stats_block():
        with ui.card().classes('w-full q-mb-md').props('flat bordered'):
            with ui.row().classes('items-center q-gutter-xl flex-wrap'):
                with ui.column().classes('items-center'):
                    ui.label(str(stats['total_messages'])).classes('text-h5 text-blue text-bold')
                    ui.label('Всего сообщений').classes('text-caption text-grey')
                with ui.column().classes('items-center'):
                    ui.label(str(stats['total_users'])).classes('text-h5 text-teal text-bold')
                    ui.label('Пользователей').classes('text-caption text-grey')
                with ui.column().classes('items-center'):
                    ui.label(str(stats['waiting_for_photo'])).classes('text-h5 text-deep-orange text-bold')
                    ui.label('Ждут фото с фасада').classes('text-caption text-grey')
                with ui.column().classes('items-center'):
                    ui.label(str(stats['photo_sent_count'])).classes('text-h5 text-green text-bold')
                    ui.label('Фото отправлено').classes('text-caption text-grey')
                ui.separator().props('vertical inset').classes('self-stretch')
                with ui.column().classes('q-gutter-xs'):
                    ui.label('Прошли этапы:').classes('text-caption text-grey')
                    with ui.row().classes('q-gutter-xs flex-wrap'):
                        for status in MessageStatus:
                            count = stats['passed_by_status'].get(status, 0)
                            color = status_colors.get(status, 'grey')
                            ui.badge(
                                f'{status_labels.get(status, status)}: {count}',
                                color=color,
                            )

    stats_block()

    columns = [
        {'name': 'id', 'label': 'ID', 'field': 'id', 'sortable': True, 'align': 'center'},
        {'name': 'text', 'label': 'Текст', 'field': 'text', 'sortable': True, 'align': 'center'},
        {'name': 'name', 'label': 'Имя', 'field': 'name', 'sortable': True, 'align': 'center'},
        {'name': 'city', 'label': 'Город', 'field': 'city', 'sortable': True, 'align': 'center'},
        {'name': 'status', 'label': 'Статус', 'field': 'status', 'sortable': True, 'align': 'center'},
        {'name': 'preview_url', 'label': 'Превью', 'field': 'preview_url', 'sortable': False, 'align': 'center'},
        {'name': 'want_photo', 'label': 'Отправить фото', 'field': 'want_photo', 'sortable': True, 'align': 'center'},
        {'name': 'shown_on_facade', 'label': 'Показано на фасаде', 'field': 'shown_on_facade', 'sortable': True, 'align': 'center'},
        {'name': 'photo_sent', 'label': 'Фото отправлено', 'field': 'photo_sent', 'sortable': True, 'align': 'center'},
        {'name': 'created_at', 'label': 'Создано', 'field': 'created_at', 'sortable': True, 'align': 'center'},
        {'name': 'actions', 'label': 'Модерация', 'field': 'actions', 'sortable': False, 'align': 'center'},
    ]

    table = ui.table(
        columns=columns,
        rows=prepare_table_rows(),
        row_key='id',
        pagination={'rowsPerPage': 100, 'sortBy': 'status_order', 'descending': False}
    ).classes('w-full')

    table.add_slot('top-right', '''
        <q-btn color="primary" icon="refresh" label="Обновить" @click="$parent.$emit('refresh')" />
    ''')

    table.add_slot('body-cell-text', '''
        <q-td :props="props">
            <div style="white-space: normal; word-break: break-word; max-width: 250px; text-align: left;">
                {{ props.row.text }}
            </div>
        </q-td>
    ''')

    table.add_slot('body-cell-status', '''
        <q-td :props="props">
            <q-badge :color="props.row.status_color">{{ props.row.status }}</q-badge>
        </q-td>
    ''')

    table.add_slot('body-cell-preview_url', '''
        <q-td :props="props">
            <q-btn
                v-if="props.row.preview_url"
                icon="image"
                color="primary"
                size="xs"
                flat
                :href="props.row.preview_url"
                target="_blank"
                type="a"
            >
                <q-tooltip>Открыть превью</q-tooltip>
            </q-btn>
            <span v-else class="text-grey">—</span>
        </q-td>
    ''')

    table.add_slot('body-cell-want_photo', '''
        <q-td :props="props">
            <q-badge :color="props.row.want_photo_color">{{ props.row.want_photo }}</q-badge>
        </q-td>
    ''')

    table.add_slot('body-cell-shown_on_facade', '''
        <q-td :props="props">
            <q-badge :color="props.row.shown_on_facade_color">{{ props.row.shown_on_facade }}</q-badge>
        </q-td>
    ''')

    table.add_slot('body-cell-photo_sent', '''
        <q-td :props="props">
            <q-badge :color="props.row.photo_sent_color">{{ props.row.photo_sent }}</q-badge>
        </q-td>
    ''')

    moderators_checkboxes = ''.join([
        f'''
        <q-checkbox
            label="{mod}"
            :model-value="props.row.vk_approvals.includes('{mod}')"
            :disable="props.row.vk_approvals.includes('{mod}') || !props.row.is_moderation_active"
            @update:model-value="(val) => val && $parent.$emit('approve', {{ message_id: props.row.id, moderator_id: '{mod}' }})"
        />
        ''' for mod in moderators
    ])

    table.add_slot('body-cell-actions', f'''
        <q-td :props="props">
            <div class="row items-center q-gutter-sm">
                {moderators_checkboxes}
                <q-btn
                    icon="close"
                    color="negative"
                    size="xs"
                    outline
                    :disable="!props.row.is_moderation_active"
                    @click="$parent.$emit('reject', props.row.id)"
                >
                    <q-tooltip>Отклонить</q-tooltip>
                </q-btn>
            </div>
        </q-td>
    ''')

    table.on('refresh', refresh_table)
    table.on('approve', lambda e: handle_vk_moderator_approve(e.args['message_id'], e.args['moderator_id']))
    table.on('reject', lambda e: handle_reject(e.args))
