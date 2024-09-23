import asyncio
from typing import List

import aiohttp
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
import pytest_asyncio
import pytest
from elasticsearch import Elasticsearch

from .settings import test_settings


@pytest_asyncio.fixture(name='es_client', scope='session')
async def es_client():
    es_client = AsyncElasticsearch(
        hosts=test_settings.es_host, verify_certs=False)
    yield es_client
    await es_client.close()


@pytest.fixture(name='es_client_sync', scope='session')
def es_client_sync():
    client = Elasticsearch(hosts=test_settings.es_host, verify_certs=False)
    yield client
    client.close()


@pytest_asyncio.fixture(name='es_write_data', scope='session')
def es_write_data(es_client: AsyncElasticsearch):
    async def inner(data: List[dict]):
        es_client_w_opt = es_client.options(request_timeout=130)
        updated, errors = await async_bulk(client=es_client_w_opt, actions=data)

        # assert updated
        if errors:
            raise Exception('Ошибка записи данных в Elasticsearch')
    return inner


@pytest_asyncio.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(name='es_session', scope='session')
async def es_session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest_asyncio.fixture(name='make_get_request', scope='session')
def make_get_request(es_session):
    async def inner(url_path: str, query_data: dict):
        url = test_settings.service_url + '/api/v1'+url_path
        async with es_session.get(url, params=query_data) as response:
            body = await response.json()
            headers = response.headers
            status = response.status
        return body, headers, status
    return inner


@pytest_asyncio.fixture(name='delete_testdata', scope='session')
def delete_testdata(es_client: AsyncElasticsearch):
    async def inner(index, test_case_prefix):
        es_client.indices.refresh(index=index)
        await es_client.delete_by_query(
            index=index,
            body={
                "query": {
                    "prefix": {
                        "id": test_case_prefix
                    }
                }
            }
        )
        es_client.indices.refresh(index=index)
    return inner


@pytest.fixture(name='delete_testdata_sync', scope='session')
def delete_testdata_sync(es_client_sync):
    async def inner(index, test_case_prefix):
        es_client_sync.indices.refresh(index=index)
        es_client_sync.delete_by_query(
            index=index,
            body={
                "query": {
                    "prefix": {
                        "id": test_case_prefix
                    }
                }
            }
        )
        es_client_sync.indices.refresh(index=index)
    return inner
