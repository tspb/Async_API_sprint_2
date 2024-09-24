from functools import lru_cache

from fastapi import Depends
from redis.asyncio import Redis
from elasticsearch import AsyncElasticsearch

from models.person import Person
from .common import CommonService

from db.elastic import get_elastic
from db.redis import get_redis


class PersonService(CommonService):
    model = Person
    index = 'persons'


@lru_cache()
def get_person_service(
        cache: Redis = Depends(get_redis),
        search_engine: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(cache, search_engine)
