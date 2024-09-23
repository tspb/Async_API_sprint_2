import json
from typing import Optional, List

from elasticsearch import AsyncElasticsearch, NotFoundError
from pydantic import BaseModel
from redis.asyncio import Redis

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class CommonService:
    model = BaseModel
    index = str

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, entity_id: str) -> Optional[BaseModel]:
        entity = await self._entity_from_cache(entity_id)
        if not entity:
            dct = await self._get_dict_from_elastic(entity_id)
            if not dct:
                return None
            entity = self.model(**dct)
            await self._put_entity_to_cache(entity)

        return entity

    async def _get_dict_from_elastic(self, entity_id: str) -> Optional[dict]:
        try:
            doc = await self.elastic.get(index=self.index, id=entity_id)
        except NotFoundError:
            return None
        return doc['_source']

    async def _entity_from_cache(self, entity_id: str) -> Optional[BaseModel]:
        cache_key = f"{self.index}:{entity_id}"
        cached_data = await self.redis.get(cache_key)
        lst = self.model.parse_raw(cached_data) if cached_data else None
        return lst

    async def _put_entity_to_cache(self, entity: BaseModel):
        await self.redis.set(f"{self.index}:{entity.id}", entity.json(), FILM_CACHE_EXPIRE_IN_SECONDS)

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

        # go to elastic
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

        results = await self.elastic.search(index=self.index, body=body)

        hits = results['hits']['hits']
        lst = [self.model(**hit['_source']) for hit in hits]

        # Сохраняем результаты в кэш
        await self.redis.set(cache_key, json.dumps([row.dict() for row in lst]), ex=FILM_CACHE_EXPIRE_IN_SECONDS)

        return lst

    async def _list_from_cache(self, cache_key) -> List[dict]:
        cached_data = await self.redis.get(cache_key)
        print(94,cached_data)
        lst=[self.model(**row) for row in json.loads(cached_data)] if cached_data and not cached_data==b'[]' else None
        # lst = self.model.parse_raw(cached_data) if cached_data and not cached_data==b'[]' else None
        return lst
