from functools import lru_cache
from typing import List

from fastapi import Depends
from redis.asyncio import Redis
from elasticsearch import AsyncElasticsearch

from models.film import Film
from .common import CommonService

from db.elastic import get_elastic
from db.redis import get_redis


class FilmService(CommonService):
    model = Film
    index = 'movies'

    async def get_films_in_genre(self, film_id: str) -> List[Film]:
        film = await self.get_by_id(film_id)
        if not film:
            return []
        films_in_genre = []
        for genre in film.genres:
            films_in_genre += await self.get_list(filter_by='genres', query=genre)
        return films_in_genre


@lru_cache()
def get_film_service(
        cache: Redis = Depends(get_redis),
        search_engine: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(cache, search_engine)
