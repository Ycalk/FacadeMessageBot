import json
import string
from redis.asyncio import Redis
from .config import Config
from aiogoogle.auth.creds import ServiceAccountCreds
from aiogoogle.resource import Method
from aiogoogle.client import Aiogoogle
from aiogoogle.resource import GoogleAPI
from shared_models.messaging.models import Message
from pydantic import BaseModel


class SheetMessage(BaseModel):
    message_id: int
    text: str
    city: str
    name: str
    approved: bool | None
    index: int


class Sheet:
    def __init__(self):
        self.redis = Redis(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            db=Config.REDIS_STORAGE_DB,
        )
        self.google_account_credentials_json = json.loads(
            Config.GOOGLE_ACCOUNT_CREDENTIALS
        )
        self.credentials = ServiceAccountCreds(
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ],
            **self.google_account_credentials_json,
        )
        self.sheet_id: int | None = None
        self.sheets_api: GoogleAPI | None = None

    async def _get_sheet_id(self) -> int:
        async with Aiogoogle(service_account_creds=self.credentials) as aiogoogle:
            sheets_api = await aiogoogle.discover("sheets", "v4")
            get_method: Method = sheets_api.spreadsheets.get  # type: ignore
            sheet_metadata = await aiogoogle.as_service_account(
                get_method(spreadsheetId=Config.GOOGLE_SHEET_ID)
            )
            return sheet_metadata["sheets"][0]["properties"]["sheetId"]  # type: ignore

    async def initialize(self):
        async with Aiogoogle(service_account_creds=self.credentials) as aiogoogle:
            self.sheet_id = await self._get_sheet_id()
            self.sheets_api = await aiogoogle.discover("sheets", "v4")

            update_method: Method = self.sheets_api.spreadsheets.values.update  # type: ignore
            cols_count = (
                5 + Config.TEAMS_COUNT * 2
            )  # 5 фиксированных + 2 колонки на каждую команду
            last_col_letter = string.ascii_uppercase[cols_count - 1]

            # Формируем заголовки
            headers = [
                "ID сообщения",
                "Текст",
                "Имя",
                "Город",
                "Обработано",
            ]
            for i in range(Config.TEAMS_COUNT):
                headers.extend(
                    [f"Команда {i + 1}", ""]
                )  # второй заголовок зальём merge'ом

            # Формируем вторую строку
            sub_headers = [""] * 5
            for _ in range(Config.TEAMS_COUNT):
                sub_headers.extend(["Утверждено", "Отклонено"])

            # Заполняем две строки
            await aiogoogle.as_service_account(
                update_method(
                    spreadsheetId=Config.GOOGLE_SHEET_ID,
                    range=f"A1:{last_col_letter}2",
                    valueInputOption="RAW",
                    json={
                        "values": [
                            headers,
                            sub_headers,
                        ]
                    },
                )
            )

            batch_update_method: Method = self.sheets_api.spreadsheets.batchUpdate  # type: ignore
            merge_requests = []

            # Объединяем первые 5 колонок (A-E) по вертикали
            for col in range(5):
                merge_requests.append(
                    {
                        "mergeCells": {
                            "range": {
                                "sheetId": self.sheet_id,
                                "startRowIndex": 0,
                                "endRowIndex": 2,
                                "startColumnIndex": col,
                                "endColumnIndex": col + 1,
                            },
                            "mergeType": "MERGE_ALL",
                        }
                    }
                )

            # Объединяем ячейки для каждой команды по горизонтали в первой строке
            for i in range(Config.TEAMS_COUNT):
                start_col = 5 + i * 2  # начальная колонка для команды i
                merge_requests.append(
                    {
                        "mergeCells": {
                            "range": {
                                "sheetId": self.sheet_id,
                                "startRowIndex": 0,
                                "endRowIndex": 1,  # только первая строка
                                "startColumnIndex": start_col,
                                "endColumnIndex": start_col + 2,  # объединяем 2 ячейки
                            },
                            "mergeType": "MERGE_ALL",
                        }
                    }
                )

            await aiogoogle.as_service_account(
                batch_update_method(
                    spreadsheetId=Config.GOOGLE_SHEET_ID,
                    json={
                        "requests": [
                            # Add protected ranges
                            {
                                "addProtectedRange": {
                                    "protectedRange": {
                                        "range": {
                                            "sheetId": self.sheet_id,
                                            "startColumnIndex": 0,
                                            "endColumnIndex": 5,
                                        },
                                        "description": "Только сервисный аккаунт может редактировать эти колонки",
                                        "warningOnly": False,
                                        "editors": {
                                            "users": [
                                                self.google_account_credentials_json[
                                                    "client_email"
                                                ]
                                            ]
                                        },
                                    }
                                }
                            },
                            {
                                "addProtectedRange": {
                                    "protectedRange": {
                                        "range": {
                                            "sheetId": self.sheet_id,
                                            "startRowIndex": 0,
                                            "endRowIndex": 2,
                                        },
                                        "description": "Только сервисный аккаунт может редактировать эту строку",
                                        "warningOnly": False,
                                        "editors": {
                                            "users": [
                                                self.google_account_credentials_json[
                                                    "client_email"
                                                ]
                                            ]
                                        },
                                    }
                                }
                            },
                            {
                                "repeatCell": {
                                    "range": {
                                        "sheetId": self.sheet_id,
                                        "startRowIndex": 0,
                                        "endRowIndex": 2,
                                        "startColumnIndex": 0,
                                        "endColumnIndex": cols_count,
                                    },
                                    "cell": {
                                        "userEnteredFormat": {
                                            "textFormat": {"bold": True},
                                            "horizontalAlignment": "CENTER",
                                            "backgroundColor": {
                                                "red": 0.9,
                                                "green": 0.9,
                                                "blue": 0.9,
                                            },
                                        }
                                    },
                                    "fields": "userEnteredFormat(textFormat,horizontalAlignment,backgroundColor)",
                                }
                            },
                            {
                                "repeatCell": {
                                    "range": {
                                        "sheetId": self.sheet_id,
                                        "startRowIndex": 0,
                                        "endRowIndex": 2,
                                        "startColumnIndex": 0,
                                        "endColumnIndex": 5,
                                    },
                                    "cell": {
                                        "userEnteredFormat": {
                                            "verticalAlignment": "MIDDLE",
                                        }
                                    },
                                    "fields": "userEnteredFormat(verticalAlignment)",
                                }
                            },
                            # Объединяем ячейки ПЕРЕД установкой frozen rows
                            *merge_requests,
                            # Title properties
                            {
                                "updateSheetProperties": {
                                    "properties": {
                                        "sheetId": self.sheet_id,
                                        "title": "Сообщения",
                                    },
                                    "fields": "title",
                                }
                            },
                            {
                                "updateDimensionProperties": {
                                    "range": {
                                        "sheetId": self.sheet_id,
                                        "dimension": "COLUMNS",
                                        "startIndex": 1,
                                        "endIndex": 2,
                                    },
                                    "properties": {"pixelSize": 300},
                                    "fields": "pixelSize",
                                }
                            },
                            # Устанавливаем frozen rows в КОНЦЕ
                            {
                                "updateSheetProperties": {
                                    "properties": {
                                        "sheetId": self.sheet_id,
                                        "gridProperties": {"frozenRowCount": 2},
                                    },
                                    "fields": "gridProperties.frozenRowCount",
                                }
                            },
                        ]
                    },
                )
            )

    async def add_message(self, message: Message):
        if not self.sheet_id:
            self.sheet_id = await self._get_sheet_id()
        if not self.sheets_api:
            async with Aiogoogle(service_account_creds=self.credentials) as aiogoogle:
                self.sheets_api = await aiogoogle.discover("sheets", "v4")

        async with Aiogoogle(service_account_creds=self.credentials) as aiogoogle:
            append_method: Method = self.sheets_api.spreadsheets.values.append  # type: ignore
            result = await aiogoogle.as_service_account(
                append_method(
                    spreadsheetId=Config.GOOGLE_SHEET_ID,
                    range="A:F",
                    valueInputOption="USER_ENTERED",
                    insertDataOption="INSERT_ROWS",
                    json={
                        "values": [
                            [
                                message.message_id,
                                message.text,
                                message.name,
                                message.city,
                                "",
                                *("" for _ in range(Config.TEAMS_COUNT * 2)),
                            ]
                        ]
                    },
                )
            )
            updated_range = result.get("updates", {}).get("updatedRange")  # type: ignore
            last_row = int(updated_range.split("!")[1][1:].split(":")[0])
            batch_update_method: Method = self.sheets_api.spreadsheets.batchUpdate  # type: ignore
            await aiogoogle.as_service_account(
                batch_update_method(
                    spreadsheetId=Config.GOOGLE_SHEET_ID,
                    json={
                        "requests": [
                            {
                                "setDataValidation": {
                                    "range": {
                                        "sheetId": self.sheet_id,
                                        "startRowIndex": last_row - 1,
                                        "endRowIndex": last_row,
                                        "startColumnIndex": 4,
                                        "endColumnIndex": 5 + Config.TEAMS_COUNT * 2,
                                    },
                                    "rule": {
                                        "condition": {"type": "BOOLEAN"},
                                        "showCustomUi": True,
                                    },
                                }
                            },
                            {
                                "repeatCell": {
                                    "range": {
                                        "sheetId": self.sheet_id,
                                        "startRowIndex": last_row - 1,
                                        "endRowIndex": last_row,
                                        "startColumnIndex": 0,
                                        "endColumnIndex": 5 + Config.TEAMS_COUNT * 2,
                                    },
                                    "cell": {
                                        "userEnteredFormat": {
                                            "textFormat": {"bold": False},
                                            "backgroundColor": {
                                                "red": 1,
                                                "green": 1,
                                                "blue": 1,
                                            },
                                        }
                                    },
                                    "fields": "userEnteredFormat(textFormat,backgroundColor)",
                                }
                            },
                            {
                                "repeatCell": {
                                    "range": {
                                        "sheetId": self.sheet_id,
                                        "startRowIndex": last_row - 1,
                                        "endRowIndex": last_row,
                                        "startColumnIndex": 0,
                                        "endColumnIndex": 4,
                                    },
                                    "cell": {
                                        "userEnteredFormat": {
                                            "verticalAlignment": "TOP",
                                            "horizontalAlignment": "LEFT",
                                            "wrapStrategy": "WRAP",
                                        }
                                    },
                                    "fields": "userEnteredFormat(verticalAlignment,horizontalAlignment,wrapStrategy)",
                                }
                            },
                        ]
                    },
                )
            )

    async def mark_as_processed(self, index: int):
        if not self.sheet_id:
            self.sheet_id = await self._get_sheet_id()
        if not self.sheets_api:
            async with Aiogoogle(service_account_creds=self.credentials) as aiogoogle:
                self.sheets_api = await aiogoogle.discover("sheets", "v4")

        async with Aiogoogle(service_account_creds=self.credentials) as aiogoogle:
            # Сначала обновляем значение в колонке "Обработано"
            update_method: Method = self.sheets_api.spreadsheets.values.update  # type: ignore
            await aiogoogle.as_service_account(
                update_method(
                    spreadsheetId=Config.GOOGLE_SHEET_ID,
                    range=f"E{index + 1}",  # Колонка E, строка index+1 (потому что индексация с 1)
                    valueInputOption="USER_ENTERED",
                    json={"values": [["TRUE"]]},
                )
            )

            # Затем защищаем всю строку от редактирования
            batch_update_method: Method = self.sheets_api.spreadsheets.batchUpdate  # type: ignore
            cols_count = 5 + Config.TEAMS_COUNT * 2

            await aiogoogle.as_service_account(
                batch_update_method(
                    spreadsheetId=Config.GOOGLE_SHEET_ID,
                    json={
                        "requests": [
                            {
                                "addProtectedRange": {
                                    "protectedRange": {
                                        "range": {
                                            "sheetId": self.sheet_id,
                                            "startRowIndex": index,
                                            "endRowIndex": index + 1,
                                            "startColumnIndex": 0,
                                            "endColumnIndex": cols_count,
                                        },
                                        "description": f"Обработанное сообщение (строка {index + 1})",
                                        "warningOnly": False,
                                        "editors": {
                                            "users": [
                                                self.google_account_credentials_json[
                                                    "client_email"
                                                ]
                                            ]
                                        },
                                    }
                                }
                            },
                            {
                                "repeatCell": {
                                    "range": {
                                        "sheetId": self.sheet_id,
                                        "startRowIndex": index,
                                        "endRowIndex": index + 1,
                                        "startColumnIndex": 0,
                                        "endColumnIndex": cols_count,
                                    },
                                    "cell": {
                                        "userEnteredFormat": {
                                            "backgroundColor": {
                                                "red": 0.95,
                                                "green": 0.95,
                                                "blue": 0.95,
                                            },
                                            "textFormat": {
                                                "foregroundColor": {
                                                    "red": 0.6,
                                                    "green": 0.6,
                                                    "blue": 0.6,
                                                },
                                            },
                                        }
                                    },
                                    "fields": "userEnteredFormat(backgroundColor,textFormat)",
                                }
                            },
                        ]
                    },
                )
            )

    async def parse_messages(self) -> list[SheetMessage]:
        if not self.sheet_id:
            self.sheet_id = await self._get_sheet_id()
        if not self.sheets_api:
            async with Aiogoogle(service_account_creds=self.credentials) as aiogoogle:
                self.sheets_api = await aiogoogle.discover("sheets", "v4")

        async with Aiogoogle(service_account_creds=self.credentials) as aiogoogle:
            get_method: Method = self.sheets_api.spreadsheets.values.get  # type: ignore

            # Получаем все данные включая колонки команд
            cols_count = 5 + Config.TEAMS_COUNT * 2
            last_col_letter = string.ascii_uppercase[cols_count - 1]

            response = await aiogoogle.as_service_account(
                get_method(
                    spreadsheetId=Config.GOOGLE_SHEET_ID,
                    range=f"A3:{last_col_letter}",  # Начинаем с 3-й строки (после заголовков)
                )
            )

            result: list[SheetMessage] = []
            values: list[list[str]] = response.get("values", [])  # type: ignore

            for row_index, row_data in enumerate(values):
                actual_row_index = (
                    row_index + 2
                )  # +2 потому что начинаем с 3-й строки (индекс 2)

                # Проверяем базовые данные сообщения
                try:
                    message_id = int(row_data[0])
                    text = row_data[1]
                    name = row_data[2]
                    city = row_data[3]
                except (IndexError, ValueError):
                    continue  # Пропускаем строки с неполными данными

                if len(row_data) > 4 and row_data[4]:
                    if row_data[4] == "TRUE":
                        continue  # Пропускаем уже обработанные сообщения

                # Определяем статус утверждения на основе решений команд

                teams_approved = 0
                teams_rejected = 0

                team_approved = False
                # Проверяем решения всех команд (начиная с колонки F, индекс 5)
                for team_index in range(Config.TEAMS_COUNT):
                    approved_col = 5 + team_index * 2  # Колонка "Утверждено"
                    rejected_col = 5 + team_index * 2 + 1  # Колонка "Отклонено"
                    team_approved = False

                    # Проверяем "Утверждено"
                    if len(row_data) > approved_col and row_data[approved_col]:
                        if row_data[approved_col] == "TRUE":
                            teams_approved += 1
                            team_approved = True

                    # Проверяем "Отклонено"
                    if len(row_data) > rejected_col and row_data[rejected_col]:
                        if row_data[rejected_col] == "TRUE":
                            if team_approved:
                                # Конфликт: обе колонки отмечены
                                teams_approved -= 1  # Отменяем засчитанное утверждение
                            else:
                                teams_rejected += 1

                approved = None
                # Определяем финальный статус
                if teams_rejected + teams_approved == Config.TEAMS_COUNT:
                    # Все команды приняли решение
                    if teams_approved == Config.TEAMS_COUNT:
                        # Все команды утвердили - сообщение утверждено
                        approved = True
                    else:
                        # Хотя бы одна команда отклонила - сообщение отклонено
                        approved = False

                result.append(
                    SheetMessage(
                        message_id=message_id,
                        text=text,
                        city=city,
                        name=name,
                        approved=approved,
                        index=actual_row_index,
                    )
                )

            return result
