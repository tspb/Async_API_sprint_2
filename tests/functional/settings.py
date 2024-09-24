from .utils.wait_for_redis import wait_for_redis
from .utils.wait_for_es import wait_for_up
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
load_dotenv('dev.env')
import os
# print(os.getenv('ELASTIC_HOST'))

class TestSettings(BaseSettings):
    es_host: str = os.getenv('ELASTIC_HOST','http://elasticsearch:9200')

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
