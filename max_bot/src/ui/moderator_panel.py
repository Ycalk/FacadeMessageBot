"""Панель модератора для управления сообщениями."""

from nicegui import ui
from sqlalchemy import select

from core.config import Config
from core.logger import get_logger
from db.models import Message, MessageStatus
from db.session import async_session
from services.internal_moderator import moderate_by_moderator

logger = get_logger(__name__)


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


@ui.page('/admin')
async def moderator_page():
    """Страница панели модератора."""

    messages = await load_messages()
    moderators = Config.moderators_list

    # Определяем цвета статусов
    status_colors = {
        MessageStatus.CREATED: 'blue',
        MessageStatus.AUTO_MODERATION: 'cyan',
        MessageStatus.INTERNAL_MODERATION: 'orange',
        MessageStatus.EXTERNAL_MODERATION: 'amber',
        MessageStatus.APPROVED: 'green',
        MessageStatus.REJECTED: 'red',
        MessageStatus.PHOTO_SENT: 'purple',
    }

    def prepare_table_rows():
        """Подготавливает данные для таблицы."""
        rows = []
        for item in messages:
            msg = item['message']
            rows.append({
                'id': msg.id,
                'image_url': msg.image_url,
                'text': msg.text or '',
                'name': msg.name,
                'city': msg.city,
                'status': msg.status,
                'status_color': status_colors.get(msg.status, 'grey'),
                'created_at': msg.created_at.strftime("%Y-%m-%d %H:%M"),
                'approvals': item['approvals'],
                'is_moderation_active': msg.status == MessageStatus.INTERNAL_MODERATION,
            })
        return rows

    async def refresh_table():
        """Обновляет данные таблицы."""
        nonlocal messages
        messages = await load_messages()
        table.rows = prepare_table_rows()
        table.update()
        ui.notify('✅ Данные обновлены', type='positive')

    async def handle_moderator_approve(message_id: int, moderator_id: str):
        """Обработчик одобрения от модератора."""
        current_msg = next((m for m in messages if m['message'].id == message_id), None)
        if not current_msg:
            return

        if moderator_id in current_msg['approvals']:
            return

        success, result = await moderate_message_by_moderator_ui(message_id, moderator_id, True)
        if success:
            ui.notify(f'✅ {moderator_id} одобрил сообщение {message_id}', type='positive')
            await refresh_table()
        else:
            ui.notify(f'❌ Ошибка: {result}', type='negative')

    async def handle_reject(message_id: int):
        """Обработчик отклонения."""
        success, result = await moderate_message_by_moderator_ui(message_id, moderators[0], False)
        if success:
            ui.notify(f'🚫 Сообщение {message_id} отклонено', type='warning')
            await refresh_table()
        else:
            ui.notify(f'❌ Ошибка: {result}', type='negative')

    ui.label('📋 Панель модератора').classes('text-h4 mb-4')

    # Определяем колонки таблицы
    columns = [
        {'name': 'id', 'label': 'ID', 'field': 'id', 'sortable': True, 'align': 'center'},
        {'name': 'image_url', 'label': 'Фото', 'field': 'image_url', 'sortable': False, 'align': 'center'},
        {'name': 'text', 'label': 'Текст', 'field': 'text', 'sortable': True, 'align': 'center'},
        {'name': 'name', 'label': 'Имя', 'field': 'name', 'sortable': True, 'align': 'center'},
        {'name': 'city', 'label': 'Город', 'field': 'city', 'sortable': True, 'align': 'center'},
        {'name': 'status', 'label': 'Статус', 'field': 'status', 'sortable': True, 'align': 'center'},
        {'name': 'created_at', 'label': 'Создано', 'field': 'created_at', 'sortable': True, 'align': 'center'},
        {'name': 'actions', 'label': 'Модерация', 'field': 'actions', 'sortable': False, 'align': 'center'},
    ]

    # Создаем таблицу с пагинацией
    table = ui.table(
        columns=columns,
        rows=prepare_table_rows(),
        row_key='id',
        pagination={'rowsPerPage': 100, 'sortBy': 'id', 'descending': True}
    ).classes('w-full')

    # Добавляем слот для кнопки обновления в топ-правый угол
    table.add_slot('top-right', '''
        <q-btn color="primary" icon="refresh" label="Обновить" @click="$parent.$emit('refresh')" />
    ''')

    # Кастомный слот для отображения фото
    table.add_slot('body-cell-image_url', '''
        <q-td :props="props">
            <a v-if="props.row.image_url" :href="props.row.image_url" target="_blank">
                <q-img :src="props.row.image_url" style="width: 30px; height: 30px" class="rounded cursor-pointer" />
            </a>
        </q-td>
    ''')

    # Кастомный слот для статуса с badge
    table.add_slot('body-cell-status', '''
        <q-td :props="props">
            <q-badge :color="props.row.status_color">{{ props.row.status }}</q-badge>
        </q-td>
    ''')

    # Кастомный слот для модерации
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

    # Обработчики событий
    table.on('refresh', refresh_table)
    table.on('approve', lambda e: handle_moderator_approve(e.args['message_id'], e.args['moderator_id']))
    table.on('reject', lambda e: handle_reject(e.args))


def init_ui(app):
    """
    Инициализация UI для интеграции с FastAPI.

    Args:
        app: FastAPI приложение
    """
    ui.run_with(
        app,
        mount_path='/ui',
        storage_secret='secret_key_for_ui',  # Замените на настоящий секретный ключ
    )
