"""Выгрузка всех пользователей в XLSX с сортировкой по created_at."""

from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path

import openpyxl
from openpyxl.styles import Font, PatternFill
from sqlalchemy import func, select

from db.models import Message, User
from db.session import async_session

_MSK = timedelta(hours=3)
_MSK_TZ = timezone(_MSK)
_HEADER_FILL = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
_HEADER_FONT = Font(bold=True, color="FFFFFF")


def _build_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Выгрузка всех пользователей в XLSX.")
    parser.add_argument(
        "--output",
        required=True,
        help="Путь к итоговому XLSX, например /home/app/data/users.xlsx",
    )
    return parser.parse_args()


async def _load_rows() -> list:
    async with async_session() as session:
        result = await session.execute(
            select(
                User.id.label("user_id"),
                User.max_id,
                User.first_name,
                User.username,
                User.created_at,
                func.count(Message.id).label("messages_count"),
            )
            .outerjoin(Message, Message.user_id == User.id)
            .group_by(
                User.id,
                User.max_id,
                User.first_name,
                User.username,
                User.created_at,
            )
            .order_by(User.created_at, User.id)
        )
        return result.all()


def _format_datetime_values(value: datetime | None) -> tuple[str, str]:
    if value is None:
        return "", ""

    if value.tzinfo is None:
        value_utc = value.replace(tzinfo=timezone.utc)
    else:
        value_utc = value.astimezone(timezone.utc)
    value_msk = value_utc.astimezone(_MSK_TZ)

    return (
        value_utc.strftime("%Y-%m-%d %H:%M:%S"),
        value_msk.strftime("%Y-%m-%d %H:%M:%S"),
    )


def _save_xlsx(rows: list, output_path: Path) -> None:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Пользователи"

    headers = [
        "user_id",
        "max_id",
        "first_name",
        "username",
        "created_at (UTC)",
        "created_at (MSK)",
        "Количество сообщений",
    ]
    widths = [10, 14, 20, 20, 22, 22, 22]

    for idx, (header, width) in enumerate(zip(headers, widths), start=1):
        cell = ws.cell(row=1, column=idx, value=header)
        cell.font = _HEADER_FONT
        cell.fill = _HEADER_FILL
        ws.column_dimensions[cell.column_letter].width = width

    ws.freeze_panes = "A2"

    for row_idx, row in enumerate(rows, start=2):
        created_at_utc, created_at_msk = _format_datetime_values(row.created_at)
        ws.cell(row=row_idx, column=1, value=row.user_id)
        ws.cell(row=row_idx, column=2, value=row.max_id)
        ws.cell(row=row_idx, column=3, value=row.first_name or "")
        ws.cell(row=row_idx, column=4, value=row.username or "")
        ws.cell(row=row_idx, column=5, value=created_at_utc)
        ws.cell(row=row_idx, column=6, value=created_at_msk)
        ws.cell(row=row_idx, column=7, value=row.messages_count)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)


async def _main() -> None:
    args = _build_args()
    rows = await _load_rows()
    output_path = Path(args.output)
    _save_xlsx(rows, output_path)
    print(f"OK: {len(rows)} строк(и) записано в {output_path}")


if __name__ == "__main__":
    asyncio.run(_main())
