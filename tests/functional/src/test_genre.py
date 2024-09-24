from typing import List
import json
import os

import pytest

from ..utils.generate_data import get_data_prefix

TESTDATA = os.path.dirname(os.path.realpath(__file__))+'/../testdata/'
pytestmark = pytest.mark.asyncio

async def test_search(make_get_request, es_write_data, es_client_sync, delete_testdata, delete_testdata_sync):
    async def get_and_check(endpoint, query_data, expected_answer):
        nonlocal case_id
        body, headers, status = await make_get_request(endpoint, query_data)

        # 4. Проверяем ответ

        assert status == expected_answer['status'], case_id
        if 'operator' in expected_answer and expected_answer['operator'] == 'gte':
            assert len(body) >= expected_answer['length']
        else:
            assert len(body) == expected_answer['length'], case_id

    # 0. Распакуем кейсы
    with open(TESTDATA+'cases_genre.json', 'r', encoding='utf-8') as f:
        cases = json.load(f)
    for case_id, case_data in cases:

        # 0.5. Удаляем старые тестовые данные
        index = case_data['index']
        es_data = case_data['input']
        if isinstance(es_data, dict):
            # упакуем в список
            es_data = [es_data,]
        assert isinstance(es_data, list)

        test_case_prefix = get_data_prefix(es_data)
        await delete_testdata(index, test_case_prefix)
        # delete_testdata_sync(index,test_case_prefix)
        # print(54, case_id, test_case_prefix)

        # 1. Генерируем данные для ES

        bulk_query: List[dict] = []
        for row in es_data:
            data = {'_index': index, '_id': row['id']}
            data.update({'_source': row})
            bulk_query.append(data)
        # print(bulk_query)

        # 2. Загружаем данные в ES
        await es_write_data(bulk_query)
        es_client_sync.indices.refresh(index=index)

        params = case_data['params']
        if isinstance(params[0], str):
            # упакуем в список, если есть только 1 вызов сервиса
            params = [params,]
        assert isinstance(params, list), params

        # 3. Запрашиваем данные из ES по API
        for param in params:  # Цикл по вызовам
            assert isinstance(param, list), params
            endpoint, query_data, expected_answer = param

            await get_and_check(endpoint, query_data, expected_answer)

            # Удалим данные из ES, но оставим в кеше.
            if 'check_cache' in case_data and case_data['check_cache']:
                # delete_testdata_sync(index,es_client_sync,test_case_prefix)
                await delete_testdata(index, test_case_prefix)
                await get_and_check(endpoint, query_data, expected_answer)

        # Удаляем тестовые данные
        # await delete_testdata(index,test_case_prefix)
        # Асинхронная версия конфликтует с другими операциями
        delete_testdata_sync(index, test_case_prefix)
