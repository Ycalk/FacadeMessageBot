"""
Конфигурация для Cities Search Service
"""
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения"""
    
    model_config = SettingsConfigDict(case_sensitive=False)
    
    # Elasticsearch settings
    elasticsearch_url: str = "http://elasticsearch:9200"
    elasticsearch_username: str = "elastic"
    elasticsearch_password: str = ""
    cities_api_token: str = ""

    # Cities data file path
    cities_file_path: str = "/home/cities/app/data/cities.csv"
    
    # API settings
    allowed_hosts: List[str] = ["*"]
    debug: bool = False
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8080
    
    @field_validator('allowed_hosts', mode='before')
    @classmethod
    def parse_allowed_hosts(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [host.strip() for host in v.split(',')]
        return v


# Создаем глобальный экземпляр настроек
settings = Settings()
