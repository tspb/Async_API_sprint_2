FROM python:3.9-slim

WORKDIR /opt/app

RUN  pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN  pip install -r requirements.txt

COPY . .

EXPOSE 8000

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV UWSGI_PROCESSES 1
ENV UWSGI_THREADS 16
ENV UWSGI_HARAKIRI 240
ENV DJANGO_SETTINGS_MODULE 'config.settings'
ENV DB_HOST=postgres
ENV DB_PORT=5432
ENV ES_SERVER_NAME=elasticsearch

RUN chmod +x entrypoint.sh


CMD ["/opt/app/entrypoint.sh"]
