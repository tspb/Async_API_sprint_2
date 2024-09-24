# Проектная работа 5 спринта
**Подготовка данных для теста (необязательно):** 
```
tests\functional>py -m utils.generate_data
```

**Запуск проекта:** 
```
cd Async_API_sprint_2
docker-compose up --build
```
Описание API будет доступно по адресу:
http://localhost:80/api/openapi/

**Запуск проекта локально:** 
```
cd Async_API_sprint_2
docker-compose -f docker-compose-local.yml up --build
cd ./FastAPI/src/
export REDIS_HOST=127.0.0.1
export ELASTIC_HOST=127.0.0.1
python3.9 -m uvicorn main:app --host 0.0.0.0

export REDIS_HOST=http://localhost:6379
export ELASTIC_HOST=http://127.0.0.1:9200
export API_SERVICE=http://localhost:8000
pytest
```
Описание API будет доступно по адресу:
http://localhost:8000/api/openapi/

Репозиторий:
https://github.com/tspb/Async_API_sprint_2