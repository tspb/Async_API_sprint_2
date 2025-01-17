from functools import lru_cache

from fastapi import Depends
from redis.asyncio import Redis
from elasticsearch import AsyncElasticsearch

from models.genre import Genre
from .common import CommonService

from db.elastic import get_elastic
from db.redis import get_redis


class GenreService(CommonService):
    model = Genre
    index = 'genres'


@lru_cache()
def get_genre_service(
        cache: Redis = Depends(get_redis),
        search_engine: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(cache, search_engine)
