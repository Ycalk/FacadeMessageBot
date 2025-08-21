import json
import asyncio
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
            await aiogoogle.as_service_account(
                update_method(
                    spreadsheetId=Config.GOOGLE_SHEET_ID,
                    range="A1:F1",
                    valueInputOption="RAW",
                    json={
                        "values": [
                            [
                                "ID сообщения",
                                "Текст",
                                "Город",
                                "Имя",
                                "Утверждено",
                                "Отклонено",
                            ]
                        ]
                    },
                )
            )
            batch_update_method: Method = self.sheets_api.spreadsheets.batchUpdate  # type: ignore
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
                                            "endColumnIndex": 4,
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
                                            "endRowIndex": 1,
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
                            # Headers properties
                            {
                                "updateSheetProperties": {
                                    "properties": {
                                        "sheetId": self.sheet_id,
                                        "gridProperties": {"frozenRowCount": 1},
                                    },
                                    "fields": "gridProperties.frozenRowCount",
                                }
                            },
                            {
                                "repeatCell": {
                                    "range": {
                                        "sheetId": self.sheet_id,
                                        "startRowIndex": 0,
                                        "endRowIndex": 1,
                                        "startColumnIndex": 0,
                                        "endColumnIndex": 6,
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
                                "",
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
                                        "endColumnIndex": 6,
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
                                        "endColumnIndex": 6,
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

    async def _clear_message_decision(self, row_index: int) -> None:
        if not self.sheet_id:
            self.sheet_id = await self._get_sheet_id()
        if not self.sheets_api:
            async with Aiogoogle(service_account_creds=self.credentials) as aiogoogle:
                self.sheets_api = await aiogoogle.discover("sheets", "v4")

        async with Aiogoogle(service_account_creds=self.credentials) as aiogoogle:
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
                                        "startRowIndex": row_index,
                                        "endRowIndex": row_index + 1,
                                        "startColumnIndex": 4,
                                        "endColumnIndex": 6,
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
                                        "startRowIndex": row_index,
                                        "endRowIndex": row_index + 1,
                                        "startColumnIndex": 4,
                                        "endColumnIndex": 6,
                                    },
                                    "cell": {"userEnteredValue": {"boolValue": False}},
                                    "fields": "userEnteredValue",
                                }
                            },
                        ]
                    },
                )
            )

    async def protect_message_decision(self, row_index: int) -> None:
        if not self.sheet_id:
            self.sheet_id = await self._get_sheet_id()
        if not self.sheets_api:
            async with Aiogoogle(service_account_creds=self.credentials) as aiogoogle:
                self.sheets_api = await aiogoogle.discover("sheets", "v4")

        async with Aiogoogle(service_account_creds=self.credentials) as aiogoogle:
            batch_update_method: Method = self.sheets_api.spreadsheets.batchUpdate  # type: ignore
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
                                            "startRowIndex": row_index,
                                            "endRowIndex": row_index + 1,
                                            "startColumnIndex": 4,
                                            "endColumnIndex": 6,
                                        },
                                        "description": "Защита от редактирования решения модератора",
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
            response = await aiogoogle.as_service_account(
                get_method(
                    spreadsheetId=Config.GOOGLE_SHEET_ID,
                    range="A2:F",
                )
            )
            result: list[SheetMessage] = []
            values: list[str] = response.get("values", [])  # type: ignore
            update_tasks = []
            for row_index, value in enumerate(values):
                row_index += 1
                try:
                    message_id = int(value[0])
                    text = value[1]
                    name = value[2]
                    city = value[3]
                except (IndexError, ValueError):
                    continue

                if (
                    len(value) != 6
                    or (value[4] == "TRUE" and value[5] == "TRUE")
                    or value[4] not in ("FALSE", "TRUE")
                    or value[5] not in ("FALSE", "TRUE")
                ):
                    approved = None
                    update_tasks.append(self._clear_message_decision(row_index))
                elif value[4] == "FALSE" and value[5] == "FALSE":
                    approved = None
                else:
                    approved = value[4] == "TRUE"
                    update_tasks.append(self.protect_message_decision(row_index))

                result.append(
                    SheetMessage(
                        message_id=message_id,
                        text=text,
                        name=name,
                        city=city,
                        approved=approved,
                    )
                )
            if update_tasks:
                await asyncio.gather(*update_tasks)
            return result
