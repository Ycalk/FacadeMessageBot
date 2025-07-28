import csv
from fuzzywuzzy import process
import httpx


class CityExtractor:
    def __init__(self, csv_file_path: str) -> None:
        self.coordinate_extractor_url = "https://nominatim.openstreetmap.org/reverse"

        with open(csv_file_path, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            self.cities = [row[0].strip().lower() for row in reader if row]

    def extract_from_text(self, text: str) -> str:
        return process.extract(text.lower(), self.cities, limit=1)[0][0].capitalize()

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
                    self.coordinate_extractor_url, params=params
                )
                data = response.json()
                return data.get("address", {}).get("city")
            except Exception:
                return None
