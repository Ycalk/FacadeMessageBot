"""
Конфигурация для Elasticsearch
"""

INDEX_NAME = "cities"

def get_elasticsearch_client():
    """Создаем и возвращаем клиент Elasticsearch"""
    from elasticsearch import Elasticsearch
    from config import settings
    kwargs = {
        "verify_certs": settings.elasticsearch_verify_certs,
    }
    if settings.elasticsearch_verify_certs and settings.elasticsearch_ca_cert:
        kwargs["ca_certs"] = settings.elasticsearch_ca_cert
    if settings.elasticsearch_password:
        return Elasticsearch(
            settings.elasticsearch_url,
            basic_auth=(settings.elasticsearch_username, settings.elasticsearch_password),
            **kwargs,
        )
    return Elasticsearch(settings.elasticsearch_url, **kwargs)

# Настройки индекса с русским анализатором
INDEX_MAPPING = {
    "settings": {
        "analysis": {
            "analyzer": {
                "russian_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "russian_stop", "russian_stemmer"]
                }
            },
            "filter": {
                "russian_stop": {
                    "type": "stop",
                    "stopwords": "_russian_"
                },
                "russian_stemmer": {
                    "type": "stemmer",
                    "language": "russian"
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "id": {"type": "integer"},
            "name": {
                "type": "text",
                "analyzer": "russian_analyzer",
                "fields": {
                    "keyword": {"type": "keyword"},
                    "suggest": {
                        "type": "completion"
                    }
                }
            }
        }
    }
}
