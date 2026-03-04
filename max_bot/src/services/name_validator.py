import csv

import httpx

from core.config import Config


class NameValidator:
    def __init__(self, csv_file_path: str):
        self.names: set[str] = set()
        with open(csv_file_path, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                if not row:
                    continue
                name = row[0].strip().lower()
                if 0 < len(name) <= Config.MAX_NAME_LENGTH:
                    self.names.add(name)

    async def validate_using_name_api(self, name: str) -> bool:
        async with httpx.AsyncClient(
            headers={"User-Agent": "name-validator/1.0"}
        ) as client:
            try:
                response = await client.post(
                    Config.NAME_API_URL,
                    params={"apiKey": Config.NAME_API_KEY},
                    json={
                        "inputPerson": {
                            "type": "NaturalInputPerson",
                            "personName": {
                                "nameFields": [
                                    {"string": name, "fieldType": "GIVENNAME"}
                                ]
                            },
                        }
                    },
                )
                data = response.json()
                if "bestMatch" in data:
                    return (
                        data["bestMatch"]["confidence"]
                        > Config.MINIMAL_NAME_CONFIDENCE
                    )
                return any(
                    match["confidence"] > Config.MINIMAL_NAME_CONFIDENCE
                    for match in data.get("matches", [])
                )
            except Exception:
                return False

    def validate_using_whitelist(self, name: str) -> bool:
        return name in self.names

    async def __call__(self, name: str) -> bool:
        name = name.strip().lower().replace("\u0451", "\u0435")
        if 0 < len(name) <= Config.MAX_NAME_LENGTH and name.isalpha():
            if self.validate_using_whitelist(name):
                return True
            if await self.validate_using_name_api(name):
                self.names.add(name)
                return True
        return False
