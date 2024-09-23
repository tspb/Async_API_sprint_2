from .utils.wait_for_redis import wait_for_redis
from .utils.wait_for_es import wait_for_up
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
load_dotenv('dev.env')


class TestSettings(BaseSettings):
    # es_host: str = Field('http://127.0.0.1:9200', env='ELASTIC_HOST')
    es_host: str = Field('http://elasticsearch:9200', env='ELASTIC_HOST')
    es_index: str = 'movies'
    es_id_field: str = 'id'
    es_index_mapping: dict = {"a": "b"}

    # redis_host: str = 'http://localhost:6379'
    redis_host: str = Field('http://redis:6379', env='REDIS_HOST')

    # service_url: str = 'http://localhost:80/api/openapi'
    api_service: str = Field('http://fastapi:80', env='API_SERVICE')

    @property
    def service_url(self) -> str:
        return f"{self.api_service}"


test_settings = TestSettings()

wait_for_up(test_settings.es_host)
wait_for_redis(test_settings.redis_host)
