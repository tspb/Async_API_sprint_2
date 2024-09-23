from faker import Faker
import json
from typing import List
from functools import lru_cache

from .__init__ import TEST_PREFIX

fake = Faker()

# TESTDATA = '../testdata/'
TESTDATA = 'testdata/'

# Добавим префикс testdata в id, чтобы удалить тестовые данные в конце тестов


def gen_test_id():
    id = fake.uuid4()
    segs = id.split('-')
    segs[0] = TEST_PREFIX
    return '-'.join(segs)


def get_set_prefix(set_id):
    set_id_str = str(set_id)
    return TEST_PREFIX[:-len(set_id_str)]+set_id_str


def gen_test_id_with_set_id(set_id):
    id = fake.uuid4()
    segs = id.split('-')
    segs[0] = get_set_prefix(set_id)
    return '-'.join(segs)


def get_data_prefix(data):
    id = data[0]['id']
    segs = id.split('-')
    return segs[0]


def get_set_id(label):
    assert label
    set_id = hash(label) % 1000
    return set_id


def get_label_prefix(label):
    return get_set_prefix(get_set_id(label))


def implement_set_id(data, set_id):
    data = data.copy()  # new object
    for i, row in enumerate(data):
        row.update({"id": gen_test_id_with_set_id(set_id)})
        for k, v in row.items():
            if TEST_PREFIX in v:
                new_val = v.replace(TEST_PREFIX, get_set_prefix(set_id))
                row.update({k: new_val})
        data[i] = row.copy()
    return data


def implement_label(data, label):
    set_id = get_set_id(label)
    return implement_set_id(data, set_id)


def multiply(data, x=2):
    data = x*data
    # Нужны новые id
    for i, row in enumerate(data):
        row.update({"id": gen_test_id()})
        data[i] = row.copy()
    return data


def save_data(test_data, file_name):
    # Преобразуем в JSON для загрузки в Elasticsearch
    test_data_json = json.dumps(test_data, ensure_ascii=False)

    print(test_data_json[:200])

    # file_path = TESTDATA+os.path.sep+file_name
    file_path = TESTDATA+file_name
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=4)

    print("Данные сохранены в "+file_path)


def generate_genre_data(num_genres, x):
    genres = []
    for _ in range(num_genres):
        genre = {
            "id": gen_test_id(),
            "name": TEST_PREFIX+''+fake.word().capitalize(),
            "description": fake.sentence()
        }
        genres.append(genre)
    genres = multiply(genres, x)
    return genres


def invalidate(entities: List[dict], field):
    entities2 = []
    for entity in entities:
        entity2 = entity.copy()
        entity2[field] = ''
        entities2.append(entity2)
    return entities2


def generate_data_2_genres():

    # 1 - подготовка данных
    # 10*2 тестовых жанров
    @lru_cache()
    def get_genres_set(label):
        test_genres = generate_genre_data(10, 2)
        return implement_label(test_genres, label)

    # 2 - подготовка запросов и ответов
    cases_genre = [
        ('test_create_genre_invalid_name', {
            'index': 'genres',
            'input': invalidate(get_genres_set('test_create_genre_invalid_name'), 'name'),
            'params': [(
                '/genre/'+row['id'],  # endpoint
                # {'id': row['id']},  # query
                {},  # query
                # {'status': 400, 'length': 0}  # response
                {'status': 200, 'length': 3}  # response
            ) for row in get_genres_set('test_create_genre_invalid_name')]
        }
        ),
        ('test_get_genre', {
            'index': 'genres',
            'input': get_genres_set('test_get_genre')[0],
            'params': (
                '/genre/'+get_genres_set('test_get_genre')[0]['id'],
                # {'id': get_genres_set('')[0]['id']},  # query
                {},  # query
                # {'status': 200, 'length': 1}  # response
                {'status': 200, 'length': 3}  # response
            )
        }
        ),
        ('test_get_nonexistent_genre', {
            'index': 'genres',
            'input': get_genres_set('test_get_nonexistent_genre')[0],
            'params': (
                '/genre/testdat0-a823-4af2-948f-30ecefbd38de',
                # {'id': "testdat0-a823-4af2-948f-30ecefbd38de"},  # query
                {},  # query
                {'status': 404, 'length': 1}  # response
            )
        }
        ),
        ('test_get_all_genres', {
            'index': 'genres',
            'input': get_genres_set('test_get_all_genres'),
            'params': (
                '/genres/',
                # {'id': TEST_PREFIX},  # query
                {'page': 1, 'per_page': 50},  # query
                {'status': 200, 'length': 20, 'operator': 'gte'}  # response
            )
        }
        ),
        ('test_get_genre_with_cache', {
            'index': 'genres',
            'input': get_genres_set('test_get_genre_with_cache')[0],
            'check_cache': True,
            'params': (
                '/genre/'+get_genres_set('test_get_genre_with_cache')[0]['id'],
                {},  # query
                {'status': 200, 'length': 3}  # response
            )
        }
        ),
    ]

    save_data(cases_genre, 'cases_genre.json')

    cases_search = [
        ('test_search_genre_size', {
            'index': 'genres',
            'input': get_genres_set('test_search_genre_size'),
            'params': (
                '/genres/',
                {'filter_by': 'id', 'query': get_label_prefix('test_search_genre_size'),
                    'page': 1, 'per_page': 4},  # query
                {'status': 200, 'length': 4}  # response
            )
        }
        ),
        ('test_search_genre', {
            'index': 'genres',
            'input': get_genres_set('test_search_genre'),
            'params': (
                '/genres/',
                {'filter_by': 'name', 'query': get_genres_set(
                    'test_search_genre')[0]['name']},  # query
                {'status': 200, 'length': 2}  # response
            )
        }
        ),
        ('test_search_genre_with_cache', {
            'index': 'genres',
            'input': get_genres_set('test_search_genre_with_cache'),
            'check_cache': True,
            'params': (
                '/genres/',
                {'filter_by': 'id', 'query': get_label_prefix('test_search_genre_with_cache'),
                    'page': 1, 'per_page': 4},  # query
                {'status': 200, 'length': 4}  # response
            )
        }
        ),
    ]
    save_data(cases_search, 'cases_search.json')


if __name__ == '__main__':
    generate_data_2_genres()
