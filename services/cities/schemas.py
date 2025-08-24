from pydantic import BaseModel, Field
from typing import Optional, List


class City(BaseModel):
    """Модель российского города"""
    id: int = Field(description="Уникальный идентификатор города", example=524901)
    name: str = Field(description="Название города на русском языке", example="Москва")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 524901,
                "name": "Москва"
            }
        }


class CityCreate(BaseModel):
    """Модель для создания нового российского города"""
    name: str = Field(description="Название города на русском языке", example="Казань")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Казань"
            }
        }


class CitySearchResponse(BaseModel):
    """Ответ на поисковый запрос российских городов"""
    cities: List[City] = Field(description="Список найденных российских городов")
    total: int = Field(description="Общее количество найденных городов", example=45)

    class Config:
        json_schema_extra = {
            "example": {
                "cities": [
                    {
                        "id": 524901,
                        "name": "Москва"
                    },
                    {
                        "id": 498817,
                        "name": "Санкт-Петербург"
                    }
                ],
                "total": 2
            }
        }


class SearchQuery(BaseModel):
    """Поисковый запрос российских городов"""
    query: str = Field(description="Поисковый запрос (название города на русском или английском)", example="Москва")
    limit: int = Field(
        default=10,
        description="Максимальное количество результатов",
        ge=1,
        le=100,
        example=10
    )

    class Config:
        json_schema_extra = {
            "example": {
                "query": "Санкт-Петербург",
                "limit": 5
            }
        }