import os
import csv


def parse_csv_cities(file_path: str, es, index_name: str) -> dict:
    """
    Парсит простой CSV файл с городами и загружает их в Elasticsearch
    
    Формат CSV файла:
    - city_name: Название города (первый столбец)
    
    Args:
        file_path: Путь к CSV файлу
        es: Объект Elasticsearch клиента
        index_name: Название индекса для загрузки
    
    Returns:
        dict: Статистика загрузки
    """
    if not os.path.exists(file_path):
        return {
            "success": False,
            "error": f"File not found: {file_path}",
            "total_lines_processed": 0,
            "cities_loaded": 0
        }

    actions = []
    batch_size = 1000
    cities_count = 0
    total_lines_processed = 0

    print(f"Loading cities from CSV: {file_path}")
    
    try:
        from elasticsearch.helpers import bulk
        with open(file_path, "r", encoding="utf-8") as file:
            # Пробуем разные разделители
            content = file.read()
            file.seek(0)
            
            # Определяем разделитель
            if ';' in content:
                delimiter = ';'
            else:
                delimiter = ','
                
            csv_reader = csv.reader(file, delimiter=delimiter)
            
            # Пропускаем заголовок
            header = next(csv_reader, None)
            if not header:
                return {
                    "success": False,
                    "error": "CSV file has no header",
                    "total_lines_processed": 0,
                    "cities_loaded": 0
                }
            
            print(f"CSV header: {header[0]}")
            
            for row in csv_reader:
                total_lines_processed += 1
                
                if not row or len(row) == 0:
                    continue
                
                try:
                    # Берем название города из первого столбца
                    city_name = row[0].strip().strip('"')
                    
                    # Проверяем что название не пустое
                    if not city_name:
                        continue

                    # Генерируем ID на основе названия
                    city_id = hash(city_name) & 0x7fffffff  # положительный int
                    
                    # Создаем документ
                    doc = {
                        "id": city_id,
                        "name": city_name
                    }
                    cities_count += 1
                    
                except (ValueError, IndexError):
                    continue

                actions.append({
                    "_index": index_name,
                    "_id": city_id,
                    "_source": doc,
                })

                if len(actions) >= batch_size:
                    bulk(es, actions, stats_only=True, request_timeout=120)
                    actions.clear()
                    print(f"Processed {total_lines_processed} lines, indexed {cities_count} cities...")

        if actions:
            bulk(es, actions, stats_only=True, request_timeout=120)
        
        print(f"=== LOADING COMPLETE ===")
        print(f"Total lines processed: {total_lines_processed}")
        print(f"Cities loaded: {cities_count}")
        print(f"========================")
        
        return {
            "success": True,
            "total_lines_processed": total_lines_processed,
            "cities_loaded": cities_count
        }
        
    except Exception as e:
        print(f"Error loading cities: {e}")
        return {
            "success": False,
            "error": str(e),
            "total_lines_processed": total_lines_processed,
            "cities_loaded": cities_count
        }