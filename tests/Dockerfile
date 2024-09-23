FROM python:3.9-slim

WORKDIR /opt/app

RUN  pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN  pip install -r requirements.txt

COPY . .

EXPOSE 8000

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV ES_SERVER_NAME=elasticsearch
ENV ELASTIC_HOST=http://elasticsearch:9200
ENV REDIS_HOST=redis

#RUN chmod +x entrypoint.sh


CMD ["pytest"]
