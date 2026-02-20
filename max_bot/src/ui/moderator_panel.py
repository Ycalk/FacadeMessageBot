"""Панель модератора для управления сообщениями."""

import hashlib
import secrets

from nicegui import app, ui
from sqlalchemy import select

from core.config import Config
from core.logger import get_logger
from db.models import Message, MessageStatus
from db.session import async_session
from services.blacklist import add_word, add_words_bulk, delete_word, get_all_words
from services.internal_moderator import moderate_by_moderator

logger = get_logger(__name__)


def _hash_password(password: str) -> str:
    """Хеширует пароль для сравнения."""
    return hashlib.sha256(password.encode()).hexdigest()


async def load_messages():
    """Загружает все сообщения из БД."""
    async with async_session() as session:
        result = await session.execute(
            select(Message)
            .order_by(Message.created_at.desc())
        )
        rows = result.scalars().all()

        messages = []
        for msg in rows:
            messages.append({
                'message': msg,
                'approvals': msg.meta.get('approvals', []) if msg.meta else [],
                'rejections': msg.meta.get('rejections', []) if msg.meta else [],
            })
        return messages


async def moderate_message_by_moderator_ui(message_id: int, moderator_id: str, approve: bool):
    """Модерация сообщения конкретным модератором."""
    try:
        result = await moderate_by_moderator(message_id, moderator_id, approve)
        logger.info(f"Модерация {message_id} от {moderator_id}: {result}")
        return result.get("success", False), result
    except Exception as e:
        logger.error(f"Ошибка при модерации сообщения {message_id}: {e}")
        return False, {"error": str(e)}


@ui.page('/admin_internal', title='Внутренняя модерация')
async def moderator_page():
    """Страница панели модератора с авторизацией."""

    # Проверяем авторизацию
    if not app.storage.user.get('auth_internal'):
        # Показываем форму входа
        with ui.card().classes('absolute-center'):
            ui.label('Вход в панель модерации').classes('text-h5 q-mb-md')
            password_input = ui.input(
                'Пароль', password=True, password_toggle_button=True
            ).classes('w-64')
            error_label = ui.label('').classes('text-negative')

            async def try_login():
                if not Config.ADMIN_INTERNAL_PASSWORD:
                    error_label.text = 'Пароль не настроен в конфигурации'
                    return
                if secrets.compare_digest(
                    _hash_password(password_input.value),
                    _hash_password(Config.ADMIN_INTERNAL_PASSWORD)
                ):
                    app.storage.user['auth_internal'] = True
                    ui.navigate.to('/admin_internal')
                else:
                    error_label.text = 'Неверный пароль'

            ui.button('Войти', on_click=try_login).classes('w-64')
            password_input.on('keydown.enter', try_login)
        return

    # === Авторизованная часть ===

    messages = await load_messages()
    moderators = Config.moderators_list

    status_colors = {
        MessageStatus.CREATED: 'blue',
        MessageStatus.AUTO_MODERATION: 'cyan',
        MessageStatus.INTERNAL_MODERATION: 'orange',
        MessageStatus.VK_MODERATION: 'teal',
        MessageStatus.MAER_MODERATION: 'amber',
        MessageStatus.APPROVED: 'green',
        MessageStatus.REJECTED: 'red',
        MessageStatus.PHOTO_SENT: 'purple',
    }

    def prepare_table_rows():
        """Подготавливает данные для таблицы."""
        rows = []
        for item in messages:
            msg = item['message']
            status_order = 0 if msg.status == MessageStatus.INTERNAL_MODERATION else 1
            want_photo = msg.want_photo
            rows.append({
                'id': msg.id,
                'status_order': status_order,
                'text': msg.text or '',
                'name': msg.name,
                'city': msg.city,
                'status': msg.status,
                'status_color': status_colors.get(msg.status, 'grey'),
                'created_at': msg.created_at.strftime("%Y-%m-%d %H:%M"),
                'approvals': item['approvals'],
                'is_moderation_active': msg.status == MessageStatus.INTERNAL_MODERATION,
                'want_photo': 'Да' if want_photo is True else ('Нет' if want_photo is False else '—'),
                'want_photo_color': 'green' if want_photo is True else ('red' if want_photo is False else 'grey'),
                'preview_url': msg.preview_url or '',
            })
        return rows

    async def refresh_table():
        """Обновляет данные таблицы."""
        nonlocal messages
        messages = await load_messages()
        table.rows = prepare_table_rows()
        table.update()
        ui.notify('Данные обновлены', type='positive')

    async def handle_moderator_approve(message_id: int, moderator_id: str):
        """Обработчик одобрения от модератора."""
        current_msg = next((m for m in messages if m['message'].id == message_id), None)
        if not current_msg:
            return

        if moderator_id in current_msg['approvals']:
            return

        success, result = await moderate_message_by_moderator_ui(message_id, moderator_id, True)
        if success:
            ui.notify(f'{moderator_id} одобрил сообщение {message_id}', type='positive')
            await refresh_table()
        else:
            ui.notify(f'Ошибка: {result}', type='negative')

    async def handle_reject(message_id: int):
        """Обработчик отклонения."""
        success, result = await moderate_message_by_moderator_ui(message_id, moderators[0], False)
        if success:
            ui.notify(f'Сообщение {message_id} отклонено', type='warning')
            await refresh_table()
        else:
            ui.notify(f'Ошибка: {result}', type='negative')

    async def logout():
        """Выход из панели."""
        app.storage.user['auth_internal'] = False
        ui.navigate.to('/admin_internal')

    # Заголовок с кнопкой выхода
    with ui.row().classes('w-full items-center justify-between mb-4'):
        ui.label('Панель модератора').classes('text-h4')
        ui.button('Выйти', on_click=logout, color='negative').props('outline size=sm')

    # Табы
    with ui.tabs().classes('w-full') as tabs:
        ui.tab('messages', label='Сообщения', icon='message')
        ui.tab('blacklist', label='Чёрный список', icon='block')

    with ui.tab_panels(tabs, value='messages').classes('w-full'):

        # ── Таб: Сообщения ──────────────────────────────────────────────────
        with ui.tab_panel('messages'):
            columns = [
                {'name': 'id', 'label': 'ID', 'field': 'id', 'sortable': True, 'align': 'center'},
                {'name': 'text', 'label': 'Текст', 'field': 'text', 'sortable': True, 'align': 'center'},
                {'name': 'name', 'label': 'Имя', 'field': 'name', 'sortable': True, 'align': 'center'},
                {'name': 'city', 'label': 'Город', 'field': 'city', 'sortable': True, 'align': 'center'},
                {'name': 'status', 'label': 'Статус', 'field': 'status', 'sortable': True, 'align': 'center'},
                {'name': 'preview_url', 'label': 'Превью', 'field': 'preview_url', 'sortable': False, 'align': 'center'},
                {'name': 'want_photo', 'label': 'Отправить фото', 'field': 'want_photo', 'sortable': True, 'align': 'center'},
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

            moderators_checkboxes = ''.join([
                f'''
                <q-checkbox
                    label="{mod}"
                    :model-value="props.row.approvals.includes('{mod}')"
                    :disable="props.row.approvals.includes('{mod}') || !props.row.is_moderation_active"
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
            table.on('approve', lambda e: handle_moderator_approve(e.args['message_id'], e.args['moderator_id']))
            table.on('reject', lambda e: handle_reject(e.args))

        # ── Таб: Чёрный список ───────────────────────────────────────────────
        with ui.tab_panel('blacklist'):
            bl_words = await get_all_words()

            def bl_rows():
                return [
                    {'id': w.id, 'word': w.word, 'created_at': w.created_at.strftime("%Y-%m-%d %H:%M")}
                    for w in bl_words
                ]

            bl_columns = [
                {'name': 'id', 'label': 'ID', 'field': 'id', 'sortable': True, 'align': 'center', 'style': 'width: 60px'},
                {'name': 'word', 'label': 'Слово / фраза', 'field': 'word', 'sortable': True, 'align': 'left'},
                {'name': 'created_at', 'label': 'Добавлено', 'field': 'created_at', 'sortable': True, 'align': 'center'},
                {'name': 'actions', 'label': '', 'field': 'actions', 'sortable': False, 'align': 'center', 'style': 'width: 60px'},
            ]

            bl_table = ui.table(
                columns=bl_columns,
                rows=bl_rows(),
                row_key='id',
                pagination={'rowsPerPage': 200, 'sortBy': 'created_at', 'descending': True},
            ).classes('w-full')

            async def bl_refresh():
                nonlocal bl_words
                bl_words = await get_all_words()
                bl_table.rows = bl_rows()
                bl_table.update()

            # top-left: поле ввода + кнопка "+"
            bl_table.add_slot('top-left', '''
                <div class="row items-center q-gutter-xs" style="padding:4px 0">
                    <input
                        id="nicegui-bl-input"
                        type="text"
                        placeholder="Слово или фраза..."
                        style="border:1px solid rgba(0,0,0,0.38);border-radius:4px;padding:6px 10px;width:220px;font-size:14px;font-family:Roboto,sans-serif;outline:none;background:transparent"
                        @keyup.enter="$parent.$emit('bl_add', $event.target.value); $event.target.value = ''"
                    />
                    <q-btn
                        icon="add" round flat size="sm" color="primary"
                        @click="const i=document.getElementById('nicegui-bl-input'); if(i){$parent.$emit('bl_add', i.value); i.value=''}"
                    >
                        <q-tooltip>Добавить</q-tooltip>
                    </q-btn>
                </div>
            ''')

            # top-right: кнопка импорта .txt через FileReader (без загрузки на сервер)
            bl_table.add_slot('top-right', '''
                <q-btn icon="upload_file" label="Импорт из файла" outline size="sm" color="primary" style="position:relative">
                    <q-tooltip>Импорт из .txt (одно слово на строку)</q-tooltip>
                    <input type="file" accept=".txt" style="position:absolute;inset:0;opacity:0;cursor:pointer;z-index:1" @change="const win=$event.target.ownerDocument.defaultView;const f=$event.target.files[0];if(!f)return;const r=new win.FileReader();r.onload=ev=>$parent.$emit('bl_import',ev.target.result);r.readAsText(f,'utf-8');$event.target.value=''"/>
                </q-btn>
            ''')

            async def on_bl_add(word: str):
                word = word.strip()
                if not word:
                    return
                result = await add_word(word)
                if result is None:
                    ui.notify(f'«{word}» уже в списке', type='warning')
                else:
                    ui.notify(f'Добавлено: «{word}»', type='positive')
                    await bl_refresh()

            async def on_bl_import(content: str):
                lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
                count = await add_words_bulk(lines)
                ui.notify(
                    f'Импортировано: {count} из {len(lines)} строк',
                    type='positive' if count > 0 else 'warning',
                )
                await bl_refresh()

            bl_table.add_slot('body-cell-actions', '''
                <q-td :props="props">
                    <q-btn
                        icon="delete"
                        color="negative"
                        size="xs"
                        flat
                        @click="$parent.$emit('bl_delete', props.row.id)"
                    >
                        <q-tooltip>Удалить</q-tooltip>
                    </q-btn>
                </q-td>
            ''')

            async def on_bl_delete(word_id: int):
                ok = await delete_word(word_id)
                if ok:
                    ui.notify('Слово удалено', type='positive')
                    await bl_refresh()
                else:
                    ui.notify('Не найдено', type='warning')

            bl_table.on('bl_add', lambda e: on_bl_add(e.args))
            bl_table.on('bl_import', lambda e: on_bl_import(e.args))
            bl_table.on('bl_delete', lambda e: on_bl_delete(e.args))
