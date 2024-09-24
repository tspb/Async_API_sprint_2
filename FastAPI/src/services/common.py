import json
from abc import ABC, abstractmethod
from typing import Optional, List, Any

from elasticsearch import AsyncElasticsearch, NotFoundError
from pydantic import BaseModel
from redis.asyncio import Redis

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class AsyncSearchEngine(ABC):
    @abstractmethod
    async def get_by_id(self, _id: str) -> Optional[Any]:
        pass

    @abstractmethod
    async def get_list(self, page: int, per_page: int) -> Optional[list[Any]]:
        pass


class Cache(ABC):
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        pass

    @abstractmethod
    async def set(self, key: str, value: str):
        pass


class ElasticAsyncSearchEngine(AsyncSearchEngine):

    def __init__(self, elastic: AsyncElasticsearch):
        self.search_engine = elastic

    async def get_by_id(self, entity_id: str) -> Optional[dict]:
        try:
            doc = await self.search_engine.get(index=self.index, id=entity_id)
        except NotFoundError:
            return None
        return doc['_source']

    async def search(
        self,
        filter_by: Optional[str],
        query: Optional[str],
        page: int = 1,
        per_page: int = 10,
        sort_by: Optional[str] = None
    ) -> List[dict]:
        body = {
            "query": {
                "bool": {
                    "must": [],
                    "filter": []
                }
            },
            "from": (page - 1) * per_page,
            "size": per_page
        }

        if filter_by and query:
            body["query"]["bool"]["must"].append(
                {"match": {f"{filter_by}": query}})

        if sort_by:
            body["sort"] = [
                {"imdb_rating": {"order": "desc" if sort_by.startswith('-') else "asc"}}]

        results = await self.search_engine.search(index=self.index, body=body)

        hits = results['hits']['hits']
        results = [hit['_source'] for hit in hits]
        return results


class CommonService(ElasticAsyncSearchEngine):
    model = BaseModel
    index = str

    def __init__(self, cache: Cache, search_engine: AsyncSearchEngine):
        self.cache = cache
        self.search_engine = search_engine

    async def get_by_id(self, entity_id: str) -> Optional[BaseModel]:
        entity = await self._entity_from_cache(entity_id)
        if not entity:
            dct = await super().get_by_id(entity_id)
            if not dct:
                return None
            entity = self.model(**dct)
            await self._put_entity_to_cache(entity)

        return entity

    async def _entity_from_cache(self, entity_id: str) -> Optional[BaseModel]:
        cache_key = f"{self.index}:{entity_id}"
        cached_data = await self.cache.get(cache_key)
        lst = self.model.parse_raw(cached_data) if cached_data else None
        return lst

    async def _put_entity_to_cache(self, entity: BaseModel):
        await self.cache.set(f"{self.index}:{entity.id}", entity.json(), FILM_CACHE_EXPIRE_IN_SECONDS)

    async def get_list(
        self,
        filter_by: Optional[str],
        query: Optional[str],
        page: int = 1,
        per_page: int = 10,
        sort_by: Optional[str] = None
    ) -> List[BaseModel]:

        # check cache
        cache_key = f"{self.index}:{filter_by}:{query}:{page}:{per_page}:{sort_by}"

        lst = await self._list_from_cache(cache_key)
        if lst:
            return lst

        # go to search_engine
        lste = await self.search(filter_by=filter_by, query=query,
                                 page=page, per_page=per_page, sort_by=sort_by)
        lst = [self.model(**item) for item in lste]

        # Сохраняем результаты в кэш
        await self.cache.set(cache_key, json.dumps([row.dict() for row in lst]), ex=FILM_CACHE_EXPIRE_IN_SECONDS)

        return lst

    async def _list_from_cache(self, cache_key) -> List[dict]:
        cached_data = await self.cache.get(cache_key)
        print(94, cached_data)
        lst = [self.model(**row) for row in json.loads(cached_data)
               ] if cached_data and not cached_data == b'[]' else None
        # lst = self.model.parse_raw(cached_data) if cached_data and not cached_data==b'[]' else None
        return lst
