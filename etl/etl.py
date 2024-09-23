import os
import fcntl
import time
from contextlib import contextmanager
from datetime import datetime
import math
import logging

import django
# Установите настройки Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
from django.db import connections, OperationalError
from django.db.models import F, Value, CharField
from django.db.models.functions import Concat
from elasticsearch import Elasticsearch, helpers

from config import settings
from state import State, JsonFileStorage
from movies.models import Genre, Person, Filmwork, GenreFilmwork, PersonFilmwork

logging.basicConfig(level=logging.INFO,
    filename="etl.log",
    filemode="w"
    )
logger = logging.getLogger(__name__)

# Инициализация клиента Elasticsearch
ES_SERVER_NAME = os.environ.get('ES_SERVER_NAME','localhost')
es = Elasticsearch(f"http://{ES_SERVER_NAME}:9200")

BATCH_SIZE = 300
LOCK_FILE = "etl.lock"
sleepSec = 60

models = (
    Genre,
    Person,
    Filmwork,
    GenreFilmwork,
    PersonFilmwork,
    )
    
person_models = (
    Person,
    )
    
genre_models = (
    Genre,
    )    
    
def extract_new_filmwork_records(model, combined_key, batch_size=BATCH_SIZE):
    wait_for_db()
        
    table_name=model._meta.db_table.lower().split('."')[1]
           
    objs = Filmwork.objects.raw(f"SELECT * FROM etl.get_film_work_by_{table_name}_key('{combined_key}', {batch_size});")
    
    # logger.info(str(objs.query)) 

    return objs
    
def extract_new_person_records(model, combined_key, batch_size=BATCH_SIZE):
    wait_for_db()
    #return None
    table_name=model._meta.db_table.lower().split('."')[1]
           
    objs = Person.objects.raw(f"SELECT * FROM etl.get_person_by_{table_name}_key('{combined_key}', {batch_size});")
    
    # logger.info(str(objs.query)) 

    return objs

def extract_new_genre_records(model, combined_key, batch_size=BATCH_SIZE):
    wait_for_db()
    '''print(76)
    from django.db import connection

    with connection.cursor() as cursor:
       cursor.execute("SELECT * FROM pg_proc WHERE proname = 'get_film_work_by_genre_film_work_key';")
       rows = cursor.fetchall()
       for row in rows:
           print(83,row)
   
    with connection.cursor() as cursor:
       cursor.execute("SELECT * FROM pg_proc WHERE proname = 'get_genre_by_genre_key';")
       rows = cursor.fetchall()
       for row in rows:
           print(89,row)
    return None'''
    table_name=model._meta.db_table.lower().split('."')[1]
           
    objs = Genre.objects.raw(f"SELECT * FROM etl.get_genre_by_{table_name}_key('{combined_key}', {batch_size});")
    #print(80,combined_key)
    #objs = Genre.objects.raw(f"SELECT * FROM etl.get_genre_by_{table_name}_key('0', {batch_size});")
    
    # logger.info(str(objs.query)) 

    return objs
    
def transform_filmworks(filmworks):
    transformed_data = []

    for filmwork in filmworks:
        genres = [g.name for g in filmwork.genres.all()]
        directors = [{"id": p.id, "name": p.full_name} for p in filmwork.persons.filter(personfilmwork__role='director')]
        actors = [{"id": p.id, "name": p.full_name} for p in filmwork.persons.filter(personfilmwork__role='actor')]
        writers = [{"id": p.id, "name": p.full_name} for p in filmwork.persons.filter(personfilmwork__role='writer')]
        
        directors_names = [p['name'] for p in directors]
        actors_names = [p['name'] for p in actors]
        writers_names = [p['name'] for p in writers]
        
        row = {
                "id": str(filmwork.id),
                "imdb_rating": filmwork.rating,
                "genres": genres,
                "title": filmwork.title,
                "description": filmwork.description,
                "directors_names": directors_names,
                "actors_names": actors_names,
                "writers_names": writers_names,
                "directors": directors,
                "actors": actors,
                "writers": writers,
                "updated_at": filmwork.updated_at.isoformat(),
            }
        transformed_data.append({
            "_index": "movies",
            "_id": str(filmwork.id),
            "_source": row
        })

    return transformed_data

def transform_persons(persons):
    transformed_data = []
    for person in persons:
        row = {
                "id": str(person.id),
                "full_name": person.full_name,
                "gender": person.gender,
        }
        transformed_data.append({
            "_index": "persons",
            "_id": str(person.id),
            "_source": row
        })
    return transformed_data
    
def transform_genres(genres):
    transformed_data = []
    for genre in genres:
        row = {
                "id": str(genre.id),
                "name": genre.name,
                "description": genre.description,
        }
        transformed_data.append({
            "_index": "genres",
            "_id": str(genre.id),
            "_source": row
        })
    return transformed_data
        
def load(transformed_data):
    #logger.info(transformed_data)
    wait_for_es()
    helpers.bulk(es, transformed_data, request_timeout=130)

def wait_for_db(initial_interval=5, max_interval=300):
    db_conn = connections['default']
    params = db_conn.get_connection_params()
    #logger.info(params)
    interval = initial_interval

    while True:
        try:
            db_conn.ensure_connection()
            break
        except OperationalError:
            logger.info(f"PostgreSQL is unavailable - sleeping for {interval} seconds")
            time.sleep(interval)
            interval = min(max_interval, interval * 2)  # Удвоение интервала до максимума

def wait_for_es(initial_interval=5, max_interval=300):
    interval = initial_interval

    while True:
        try:
            if es.ping():
                break
        except ElasticsearchException:
            pass
        logger.info(f"Elasticsearch is unavailable - sleeping for {interval} seconds")
        time.sleep(interval)
        interval = min(max_interval, interval * 2)  # Удвоение интервала до максимума
        
def acquire_lock():
    lock_file = open(LOCK_FILE, 'w')
    try:
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return lock_file
    except IOError:
        logger.info("Another instance of the ETL process is running. Exiting.")
        exit(1)
        
def release_lock(lock_file):
    fcntl.flock(lock_file, fcntl.LOCK_UN)
    lock_file.close()

def etl_process():
    lock_file = acquire_lock()
    try:
        #outer loop (batch loop)
        while True:
            for model in models:#inner loop (model loop)                
                # get last_processed_combined_key for model from stored state
                last_processed_combined_key=None
                state_dict = state.get_state(model.__name__)
                if state_dict:
                    combined_key = state_dict['last_processed_combined_key']
                else:
                    combined_key = ''
                
                # process filmworks
                filmwork_objs = extract_new_filmwork_records(model,combined_key)
                if filmwork_objs:
                    last_processed_combined_key = filmwork_objs[0].max_in_combined_key
                    
                    transformed_data = transform_filmworks(filmwork_objs)
                
                    load(transformed_data)
                
                # process persons
                if model in person_models:
                    person_objs = extract_new_person_records(model, combined_key)
                    if person_objs:
                        transformed_data = transform_persons(person_objs)
                        load(transformed_data)
                        
                # process genres
                if model in genre_models:
                    genre_objs = extract_new_genre_records(model, combined_key)
                    if genre_objs:
                        transformed_data = transform_genres(genre_objs)
                        load(transformed_data)                        
                # is this the end?
                if not filmwork_objs:
                    logger.info("No more data to process. ETL-process finished.")
                    break# this inner, then outer loops
                
                # store last_processed_combined_key
                
                state.set_state(model.__name__, {
                    'last_processed_combined_key':last_processed_combined_key
                    }
                )
                logger.info(f"Processed: {model.__name__}: {last_processed_combined_key}")
            else:
                continue# outer loop, normal continuation
            break# outer loop after inner loop breaked
    finally:
        release_lock(lock_file)            

if __name__ == "__main__":
    storage = JsonFileStorage('etl_state.json')
    state = State(storage)
    while True:
        etl_process()
        # Ждем 1 минуту обновлений в источнике
        time.sleep(sleepSec)