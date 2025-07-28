import csv
from ..config import Config
import httpx


class NameValidator:
    def __init__(self, csv_file_path: str):
        with open(csv_file_path, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            with open(csv_file_path, mode="r", encoding="utf-8") as file:
                reader = csv.reader(file)
                self.names: set[str] = set()
                for row in reader:
                    if not row or len(row) == 0:
                        continue
                    city = row[0].strip().lower()
                    if len(city) < Config.MAX_NAME_LENGTH:
                        self.names.add(city)

    async def validate_using_name_api(self, name: str) -> bool:
        async with httpx.AsyncClient(
            headers={"User-Agent": "city-extractor-script/1.0"}
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
                        data["bestMatch"]["confidence"] > Config.MINIMAL_NAME_CONFIDENCE
                    )
                return any(
                    match["confidence"] > Config.MINIMAL_NAME_CONFIDENCE
                    for match in data["matches"]
                )
            except Exception:
                return False

    def validate_using_whitelist(self, name: str) -> bool:
        return name in self.names

    async def __call__(self, name: str) -> bool:
        name = name.strip().lower().replace("ё", "е")
        if len(name) < Config.MAX_NAME_LENGTH and len(name) > 0 and name.isalpha():
            if self.validate_using_whitelist(name):
                return True
            elif await self.validate_using_name_api(name):
                self.names.add(name)
                return True
        return False
