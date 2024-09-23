FROM postgres:16

# Определяем переменные среды для настройки базы данных
ENV POSTGRES_DB=postgres
ENV POSTGRES_USER=postgres

# Открываем порт для подключения к базе данных
EXPOSE 5432

VOLUME /var/lib/postgresql/data

# Добавляем скрипты инициализации для создания пользователя "app"
COPY pg_init /docker-entrypoint-initdb.d/
RUN chown -R postgres:postgres /docker-entrypoint-initdb.d/

