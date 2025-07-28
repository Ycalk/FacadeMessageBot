import csv
from thefuzz import process
import httpx
from ..config import Config


class CityExtractor:
    def __init__(self, csv_file_path: str) -> None:
        with open(csv_file_path, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            self.cities: list[str] = []
            for row in reader:
                if not row or len(row) == 0:
                    continue
                city = row[0].strip().lower()
                if len(city) < Config.MAX_CITY_LENGTH:
                    self.cities.append(city)

    def extract_from_text(self, text: str) -> str:
        return process.extractOne(text.lower().strip(), self.cities)[0].capitalize()

    async def extract_from_coordinates(
        self, latitude: float, longitude: float
    ) -> str | None:
        async with httpx.AsyncClient(
            headers={"User-Agent": "city-extractor-script/1.0"}
        ) as client:
            params = {
                "lat": str(latitude),
                "lon": str(longitude),
                "format": "json",
            }
            try:
                response = await client.get(
                    Config.COORDINATE_EXTRACTOR_URL, params=params
                )
                data = response.json()
                city = data.get("address", {}).get("city")
                if len(city) < Config.MAX_CITY_LENGTH:
                    return city.capitalize()
            except Exception:
                return None
