"""Панель модератора для управления сообщениями."""

import asyncio
import csv
import io
import json
import secrets
from datetime import date, datetime, timedelta

from nicegui import app, ui
from sqlalchemy import select

from core.config import Config
from core.logger import get_logger
from db.models import Message, MessageStatus
from db.session import async_session
from services.app_settings import (
    DEFAULT_MISTRAL_PROMPT,
    MARCH_REMINDER_SENT_KEY,
    MISTRAL_PROMPT_KEY,
    STREAM_URL_KEY,
    get_auto_approve_moderators,
    get_setting,
    set_auto_approve_moderators,
    set_setting,
)
from services.broadcast import send_march_reminder
from services.stats import build_message_log_xlsx, load_hourly_stats, load_stats
from services.blacklist import add_word, add_words_bulk, delete_word, get_all_words
from services.internal_moderator import moderate_by_moderator
from services.smartcaptcha import validate_smartcaptcha_token

logger = get_logger(__name__)

_MSK = timedelta(hours=3)


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

    ui.add_head_html(
        '''
        <script src="https://smartcaptcha.cloud.yandex.ru/captcha.js" defer></script>
        <script>
            window.__smartCaptchaTokens = window.__smartCaptchaTokens || {};
            window.__initSmartCaptchaWidget = window.__initSmartCaptchaWidget || async function(containerId, sitekey) {
                const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
                for (let i = 0; i < 30; i++) {
                    if (!window.smartCaptcha) {
                        await delay(150);
                        continue;
                    }
                    const container = document.getElementById(containerId);
                    if (!container) return false;
                    if (container.dataset.widgetId) return true;
                    try {
                        const widgetId = window.smartCaptcha.render(container, {
                            sitekey: sitekey,
                            hl: 'ru',
                            callback: function(token) {
                                window.__smartCaptchaTokens[containerId] = token;
                            }
                        });
                        container.dataset.widgetId = String(widgetId);
                        return true;
                    } catch (e) {
                        console.error('SmartCaptcha render error', e);
                        return false;
                    }
                }
                return false;
            };

            window.__getSmartCaptchaToken = window.__getSmartCaptchaToken || async function(containerId) {
                const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
                const container = document.getElementById(containerId);
                if (!container) return '';

                let token = window.__smartCaptchaTokens[containerId] || '';
                const widgetId = Number(container.dataset.widgetId || 'NaN');
                if (!token && window.smartCaptcha && Number.isFinite(widgetId)) {
                    try {
                        await window.smartCaptcha.execute(widgetId);
                        for (let i = 0; i < 40; i++) {
                            token = window.__smartCaptchaTokens[containerId] || '';
                            if (token) break;
                            await delay(100);
                        }
                    } catch (e) {
                        console.error('SmartCaptcha execute error', e);
                    }
                }
                return token || '';
            };

            window.__resetSmartCaptcha = window.__resetSmartCaptcha || function(containerId) {
                const container = document.getElementById(containerId);
                if (!container) return false;
                window.__smartCaptchaTokens[containerId] = '';
                const widgetId = Number(container.dataset.widgetId || 'NaN');
                if (window.smartCaptcha && Number.isFinite(widgetId)) {
                    try {
                        window.smartCaptcha.reset(widgetId);
                    } catch (e) {
                        console.error('SmartCaptcha reset error', e);
                        return false;
                    }
                }
                return true;
            };
        </script>
        '''
    )

    # Проверяем авторизацию
    if not app.storage.user.get('auth_internal'):
        # Показываем форму входа
        with ui.card().classes('absolute-center'):
            ui.label('Вход в панель модерации').classes('text-h5 q-mb-md')
            with ui.column().classes('w-[400px] max-w-full'):
                username_input = ui.input('Логин').classes('w-full')
                password_input = ui.input(
                    'Пароль', password=True, password_toggle_button=True
                ).classes('w-full')
                if Config.SMARTCAPTCHA_CLIENT_KEY:
                    ui.html(
                        f'<div id="captcha-container-internal" class="smart-captcha" '
                        f'data-sitekey="{Config.SMARTCAPTCHA_CLIENT_KEY}"></div>'
                    ).classes('w-full').style('min-height: 100px;')
                    await ui.run_javascript(
                        f"return window.__initSmartCaptchaWidget('captcha-container-internal', {json.dumps(Config.SMARTCAPTCHA_CLIENT_KEY)});"
                    )
                else:
                    ui.label('SMARTCAPTCHA_CLIENT_KEY не задан').classes('text-negative text-caption w-full')
                error_label = ui.label('').classes('text-negative w-full')

                async def try_login():
                    username = (username_input.value or '').strip()
                    password = password_input.value or ''
                    credentials = Config.admin_internal_credentials

                    if not Config.SMARTCAPTCHA_CLIENT_KEY:
                        error_label.text = 'Капча не настроена в конфигурации'
                        return

                    captcha_token = await ui.run_javascript(
                        "return window.__getSmartCaptchaToken('captcha-container-internal');"
                    )
                    captcha_ok, captcha_error = await validate_smartcaptcha_token(captcha_token)
                    if not captcha_ok:
                        error_label.text = captcha_error
                        await ui.run_javascript("return window.__resetSmartCaptcha('captcha-container-internal');")
                        return

                    if not credentials:
                        error_label.text = 'Учётные записи не настроены в конфигурации'
                        return

                    expected_password = credentials.get(username)
                    if expected_password and secrets.compare_digest(password, expected_password):
                        app.storage.user['auth_internal'] = True
                        app.storage.user['auth_internal_user'] = username
                        ui.navigate.to('/admin_internal')
                    else:
                        error_label.text = 'Неверный логин или пароль'
                        await ui.run_javascript("return window.__resetSmartCaptcha('captcha-container-internal');")

                ui.button('Войти', on_click=try_login).classes('w-full')
                username_input.on('keydown.enter', try_login)
                password_input.on('keydown.enter', try_login)
        return

    # === Авторизованная часть ===

    messages = await load_messages()
    moderators = Config.moderators_list
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

    def format_dt_msk(value) -> str:
        """Форматирует datetime в UTC+3 для отображения в таблице."""
        if value is None:
            return '—'
        return (value + _MSK).strftime("%Y-%m-%d %H:%M")

    def prepare_table_rows():
        """Подготавливает данные для таблицы."""
        rows = []
        for item in messages:
            msg = item['message']
            status_order = 0 if msg.status == MessageStatus.INTERNAL_MODERATION else 1
            want_photo = msg.want_photo
            shown_on_facade = msg.shown_on_facade
            photo_sent = msg.photo_sent
            reminder_sent = msg.reminder_sent
            rows.append({
                'id': msg.id,
                'status_order': status_order,
                'text': msg.text or '',
                'name': msg.name,
                'city': msg.city,
                'status': msg.status,
                'status_color': status_colors.get(msg.status, 'grey'),
                'created_at': (msg.created_at + _MSK).strftime("%Y-%m-%d %H:%M"),
                'shown_time': format_dt_msk(msg.shown_time),
                'approvals': item['approvals'],
                'is_moderation_active': msg.status == MessageStatus.INTERNAL_MODERATION,
                'want_photo': 'Да' if want_photo is True else ('Нет' if want_photo is False else '—'),
                'want_photo_color': 'green' if want_photo is True else ('red' if want_photo is False else 'grey'),
                'shown_on_facade': 'Да' if shown_on_facade else 'Нет',
                'shown_on_facade_color': 'deep-purple' if shown_on_facade else 'grey',
                'photo_sent': 'Да' if photo_sent else 'Нет',
                'photo_sent_color': 'green' if photo_sent else 'grey',
                'reminder_sent': 'Да' if reminder_sent else 'Нет',
                'reminder_sent_color': 'green' if reminder_sent else 'grey',
                'preview_url': msg.preview_url or '',
            })
        return rows

    async def refresh_table():
        """Обновляет данные таблицы и статистику."""
        nonlocal messages, stats
        messages = await load_messages()
        stats = await load_stats()
        table.rows = prepare_table_rows()
        table.update()
        stats_block.refresh()
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
        app.storage.user['auth_internal_user'] = None
        ui.navigate.to('/admin_internal')

    # Заголовок с кнопкой выхода
    with ui.row().classes('w-full items-center justify-between mb-4'):
        ui.label('Панель модератора').classes('text-h4')
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
                    ui.label(str(stats['message_input_attempts'])).classes('text-h5 text-indigo text-bold')
                    ui.label('Попыток ввода').classes('text-caption text-grey')
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

    # Табы
    with ui.tabs().classes('w-full') as tabs:
        ui.tab('messages', label='Сообщения', icon='message')
        ui.tab('blacklist', label='Чёрный список', icon='block')
        ui.tab('prompt', label='Промпт Mistral', icon='psychology')
        ui.tab('broadcast', label='Рассылка', icon='campaign')
        ui.tab('stats', label='Статистика', icon='bar_chart')

    with ui.tab_panels(tabs, value='messages').classes('w-full'):

        # ── Таб: Сообщения ──────────────────────────────────────────────────
        with ui.tab_panel('messages'):
            # Панель автоодобрения
            auto_approve_mods = await get_auto_approve_moderators()

            with ui.card().classes('w-full q-mb-md').props('flat bordered'):
                with ui.row().classes('items-center q-gutter-md'):
                    ui.label('Автоодобрение:').classes('text-caption text-grey')
                    for mod in moderators:
                        switch = ui.switch(mod, value=mod in auto_approve_mods)

                        async def on_toggle(e, moderator_id: str = mod):
                            enabled = e.value
                            mods = await get_auto_approve_moderators()
                            if enabled:
                                mods.add(moderator_id)
                            else:
                                mods.discard(moderator_id)
                            await set_auto_approve_moderators(mods)
                            ui.notify(
                                f'Автоодобрение {"включено" if enabled else "выключено"}: {moderator_id}',
                                type='positive' if enabled else 'warning',
                            )

                        switch.on_value_change(on_toggle)

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
                {'name': 'reminder_sent', 'label': 'Напоминание', 'field': 'reminder_sent', 'sortable': True, 'align': 'center'},
                {'name': 'shown_time', 'label': 'Факт показа (МСК)', 'field': 'shown_time', 'sortable': True, 'align': 'center'},
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

            table.add_slot('body-cell-reminder_sent', '''
                <q-td :props="props">
                    <q-badge :color="props.row.reminder_sent_color">{{ props.row.reminder_sent }}</q-badge>
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
                    {'id': w.id, 'word': w.word, 'created_at': (w.created_at + _MSK).strftime("%Y-%m-%d %H:%M")}
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

        # ── Таб: Промпт Mistral ──────────────────────────────────────────────
        with ui.tab_panel('prompt'):
            current_prompt = await get_setting(MISTRAL_PROMPT_KEY, DEFAULT_MISTRAL_PROMPT)

            ui.label('Правила модерации Mistral').classes('text-subtitle1 q-mb-xs')
            ui.label('Изменения применяются сразу после сохранения.').classes('text-caption text-grey q-mb-md')

            prompt_area = ui.textarea(
                value=current_prompt,
            ).classes('w-full').props('rows=20 outlined')

            async def save_prompt():
                await set_setting(MISTRAL_PROMPT_KEY, prompt_area.value)
                ui.notify('Промпт сохранён', type='positive')

            with ui.row().classes('q-mt-sm items-center q-gutter-sm'):
                ui.button('Сохранить', icon='save', on_click=save_prompt, color='primary')
                ui.button(
                    'Сбросить к дефолту',
                    icon='restart_alt',
                    on_click=lambda: prompt_area.set_value(DEFAULT_MISTRAL_PROMPT),
                    color='grey',
                ).props('outline')

        # ── Таб: Рассылка ────────────────────────────────────────────────────
        with ui.tab_panel('broadcast'):
            current_stream_url = await get_setting(STREAM_URL_KEY, '')
            last_sent = await get_setting(MARCH_REMINDER_SENT_KEY, '')

            ui.label('Рассылка напоминания').classes('text-subtitle1 q-mb-xs')
            ui.label(
                'Сообщение будет отправлено всем пользователям с одобренными поздравлениями, '
                'кому напоминание ещё не отправлялось.'
            ).classes('text-caption text-grey q-mb-md')

            stream_url_input = ui.input(
                label='Ссылка на прямую трансляцию',
                value=current_stream_url,
                placeholder='https://...',
            ).classes('w-full').props('outlined')

            sent_label_text = f'Последняя рассылка: {last_sent}' if last_sent else 'Рассылка ещё не выполнялась'
            sent_label = ui.label(sent_label_text).classes('text-caption text-grey q-mt-sm')
            broadcast_btn = ui.button(
                'Отправить напоминание',
                icon='send',
                color='primary',
            ).classes('q-mt-md')

            async def _broadcast_task(url: str) -> None:
                """Фоновый таск рассылки — обновляет UI по завершению."""
                try:
                    count = await send_march_reminder(url)
                    new_sent = await get_setting(MARCH_REMINDER_SENT_KEY, '')
                    sent_label.text = f'Последняя рассылка: {new_sent} ({count} отправлено)'
                except Exception as e:
                    logger.error(f'Ошибка рассылки: {e}')
                    sent_label.text = f'Ошибка рассылки: {e}'
                finally:
                    broadcast_btn.enable()

            async def do_broadcast():
                url = stream_url_input.value.strip()
                if not url:
                    ui.notify('Укажите ссылку на трансляцию', type='warning')
                    return
                await set_setting(STREAM_URL_KEY, url)
                broadcast_btn.disable()
                sent_label.text = 'Рассылка выполняется...'
                asyncio.create_task(_broadcast_task(url))

            broadcast_btn.on_click(do_broadcast)

        # ── Таб: Статистика ──────────────────────────────────────────────────
        with ui.tab_panel('stats'):
            ui.label('Сообщения по часам').classes('text-subtitle1 q-mb-xs')
            ui.label('Выберите день и скачайте CSV с разбивкой по часам.').classes('text-caption text-grey q-mb-md')

            today_str = date.today().strftime('%Y-%m-%d')
            date_input = ui.input(
                label='Дата',
                value=today_str,
                placeholder='YYYY-MM-DD',
            ).classes('w-48').props('outlined')
            with date_input:
                with ui.menu() as date_menu:
                    date_picker = ui.date(value=today_str).props('minimal')
                    date_picker.on_value_change(lambda e: (
                        date_input.set_value(e.value),
                        date_menu.close(),
                    ))
                ui.button(icon='event', on_click=date_menu.open).props('flat dense')

            async def export_csv():
                raw = date_input.value.strip()
                try:
                    target = date.fromisoformat(raw)
                except ValueError:
                    ui.notify('Неверный формат даты, используйте YYYY-MM-DD', type='negative')
                    return

                rows = await load_hourly_stats(target)

                buf = io.StringIO()
                writer = csv.DictWriter(buf, fieldnames=['час', 'сообщений'], delimiter=';')
                writer.writeheader()
                writer.writerows(rows)

                filename = f'messages_by_hour_{target.isoformat()}.csv'
                ui.download.content(buf.getvalue().encode('utf-8-sig'), filename)
                ui.notify(f'CSV готов: {filename}', type='positive')

            ui.button('Скачать CSV', icon='download', on_click=export_csv, color='primary').classes('q-mt-md')

            ui.separator().classes('q-my-lg')

            ui.label('Выгрузка лога сообщений').classes('text-subtitle1 q-mb-xs')
            ui.label('Все попытки ввода текста за период (из message_input_logs).').classes('text-caption text-grey q-mb-md')

            with ui.row().classes('items-end q-gutter-md flex-wrap'):
                _today = date.today().strftime('%Y-%m-%d')

                # ── С (дата + время) ──────────────────────────────────────────
                with ui.row().classes('items-end q-gutter-xs no-wrap'):
                    log_from_date_input = ui.input(label='С (дата)', value=_today, placeholder='YYYY-MM-DD').classes('w-36').props('outlined')
                    with log_from_date_input:
                        with ui.menu() as log_from_date_menu:
                            _p = ui.date(value=_today).props('minimal')
                            _p.on_value_change(lambda e: (
                                log_from_date_input.set_value(e.value),
                                log_from_date_menu.close(),
                            ))
                        ui.button(icon='event', on_click=log_from_date_menu.open).props('flat dense')

                    log_from_time_input = ui.input(label='Время', value='00:00', placeholder='HH:MM').classes('w-24').props('outlined')
                    with log_from_time_input:
                        with ui.menu() as log_from_time_menu:
                            _tp = ui.time(value='00:00').props('format24h')
                            _tp.on_value_change(lambda e: (
                                log_from_time_input.set_value(e.value),
                                log_from_time_menu.close(),
                            ))
                        ui.button(icon='schedule', on_click=log_from_time_menu.open).props('flat dense')

                # ── По (дата + время) ─────────────────────────────────────────
                with ui.row().classes('items-end q-gutter-xs no-wrap'):
                    log_to_date_input = ui.input(label='По (дата)', value=_today, placeholder='YYYY-MM-DD').classes('w-36').props('outlined')
                    with log_to_date_input:
                        with ui.menu() as log_to_date_menu:
                            _p2 = ui.date(value=_today).props('minimal')
                            _p2.on_value_change(lambda e: (
                                log_to_date_input.set_value(e.value),
                                log_to_date_menu.close(),
                            ))
                        ui.button(icon='event', on_click=log_to_date_menu.open).props('flat dense')

                    log_to_time_input = ui.input(label='Время', value='23:59', placeholder='HH:MM').classes('w-24').props('outlined')
                    with log_to_time_input:
                        with ui.menu() as log_to_time_menu:
                            _tp2 = ui.time(value='23:59').props('format24h')
                            _tp2.on_value_change(lambda e: (
                                log_to_time_input.set_value(e.value),
                                log_to_time_menu.close(),
                            ))
                        ui.button(icon='schedule', on_click=log_to_time_menu.open).props('flat dense')

                async def export_log_xlsx():
                    try:
                        dt_from = datetime.fromisoformat(
                            f'{log_from_date_input.value.strip()} {log_from_time_input.value.strip()}:00'
                        )
                        dt_to = datetime.fromisoformat(
                            f'{log_to_date_input.value.strip()} {log_to_time_input.value.strip()}:59'
                        )
                    except ValueError:
                        ui.notify('Неверный формат даты/времени', type='negative')
                        return
                    if dt_from > dt_to:
                        ui.notify('Дата «С» не может быть позже даты «По»', type='negative')
                        return

                    xlsx_bytes = await build_message_log_xlsx(dt_from, dt_to)
                    suffix = f'{dt_from.strftime("%Y%m%d_%H%M")}_{dt_to.strftime("%Y%m%d_%H%M")}'
                    filename = f'message_log_{suffix}.xlsx'
                    ui.download.content(xlsx_bytes, filename)
                    ui.notify(f'Файл готов: {filename}', type='positive')

                ui.button('Скачать XLSX', icon='download', on_click=export_log_xlsx, color='secondary')
