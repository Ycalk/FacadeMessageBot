"""
API роуты для Cities Search Service
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
import os

from schemas import City, CitySearchResponse, SearchQuery
from es_client import get_elasticsearch_client, INDEX_NAME
from utils import parse_csv_cities

router = APIRouter()


@router.post("/search", response_model=CitySearchResponse, tags=["cities"],
             summary="Поиск российских городов",
             description="Поиск городов по русскому названию с использованием нечёткого поиска. "
                        "Результаты сортируются по релевантности.")
async def search_cities(query: SearchQuery):
    q = query.query

    es_query = {
        "bool": {
            "should": [
                {
                    "term": {
                        "name.keyword": {
                            "value": q,
                            "boost": 10
                        }
                    }
                },
                {
                    "match": {
                        "name": {
                            "query": q,
                            "analyzer": "russian_analyzer",
                            "operator": "and",
                            "minimum_should_match": "80%",
                            "auto_generate_synonyms_phrase_query": False,
                            "boost": 5
                        }
                    }
                },
                {
                    "match": {
                        "name": {
                            "query": q,
                            "fuzziness": 2,
                            "prefix_length": 1,
                            "auto_generate_synonyms_phrase_query": False,
                            "boost": 0.3
                        }
                    }
                }
            ],
            "minimum_should_match": 1
        }
    }

    try:
        es = get_elasticsearch_client()
        resp = es.search(
            index=INDEX_NAME,
            query=es_query,
            size=query.limit,
            sort=["_score"],
            request_timeout=10,
        )
        cities = [City(**hit["_source"]) for hit in resp["hits"]["hits"]]
        return CitySearchResponse(cities=cities, total=resp["hits"]["total"]["value"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload", tags=["cities"],
             summary="Загрузить CSV файл с городами",
             description="""
             Загружает новые города из CSV файла в базу данных.
             
             **Формат CSV файла (разделитель: ';' или ','):**
             ```
             city_name
             Москва
             Санкт-Петербург
             Казань
             ```
             
             **Поля:**
             - `city_name` - **Название города** (обязательное, первый столбец)
             
             Просто список городов, по одному на строку.
             
             Файл должен содержать заголовок в первой строке.
             """)
async def upload_cities_csv(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV file")
    
    # Сохраняем временный файл
    temp_path = f"/tmp/{file.filename}"
    try:
        with open(temp_path, "wb") as temp_file:
            content = await file.read()
            temp_file.write(content)
        
        # Парсим и загружаем
        es = get_elasticsearch_client()
        result = parse_csv_cities(temp_path, es, INDEX_NAME)
        
        # Удаляем временный файл
        os.remove(temp_path)
        
        if result["success"]:
            return {
                "message": "Cities uploaded successfully",
                "total_lines_processed": result["total_lines_processed"],
                "cities_loaded": result["cities_loaded"]
            }
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except Exception as e:
        # Очищаем временный файл в случае ошибки
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", tags=["health"],
            summary="Статистика загруженных данных",
            description="Показывает количество загруженных городов в Elasticsearch")
async def get_stats():
    try:
        es = get_elasticsearch_client()
        count_resp = es.count(index=INDEX_NAME)
        total_cities = count_resp["count"]
        return {
            "total_cities": total_cities,
            "index_name": INDEX_NAME,
            "status": "healthy"
        }
    except Exception as e:
        return {
            "total_cities": 0,
            "index_name": INDEX_NAME,
            "status": "error",
            "error": str(e)
        }