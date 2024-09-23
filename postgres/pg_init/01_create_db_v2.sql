create role app with login password '123qwe';
GRANT postgres TO app;
alter user app createdb;
ALTER USER app WITH SUPERUSER;
ALTER USER app WITH LOGIN;

\c postgres app;
CREATE DATABASE movies_database;
