import httpx
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class City:
    id: int
    name: str


@dataclass
class CitySearchResponse:
    cities: List[City]
    total: int


class CitiesClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient()

    async def search_cities(self, query: str, limit: int = 5) -> Optional[CitySearchResponse]:
        """Search for cities using the cities service API"""
        try:
            response = await self.client.post(
                f"{self.base_url}/cities/search",
                json={"query": query, "limit": limit},
                timeout=5.0
            )
            response.raise_for_status()
            data = response.json()
            
            cities = [City(id=city["id"], name=city["name"]) for city in data["cities"]]
            return CitySearchResponse(cities=cities, total=data["total"])
        except Exception:
            return None

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()