\c movies_database app;
CREATE SCHEMA IF NOT EXISTS etl;
/*
DROP VIEW etl.film_work_v;
DROP VIEW etl.person_v;
DROP VIEW etl.genre_v;
DROP VIEW etl.person_film_work_v;
DROP VIEW etl.genre_film_work_v;
DROP FUNCTION etl.get_film_work_by_person_key;
DROP FUNCTION etl.get_film_work_by_film_work_key;
DROP FUNCTION etl.get_film_work_by_genre_key;
DROP FUNCTION etl.get_film_work_by_person_film_work_key;
DROP FUNCTION etl.get_film_work_by_genre_film_work_key;
*/
CREATE OR REPLACE VIEW etl.film_work_v
AS 
SELECT t.*, ((EXTRACT(epoch FROM updated_at)::float)::text || '-' || id)::text  combined_key
FROM content.film_work t;


CREATE OR REPLACE VIEW etl.person_v
AS 
SELECT t.*, ((EXTRACT(epoch FROM updated_at)::float)::text || '-' || id)::text  combined_key
FROM content.person t;


CREATE OR REPLACE VIEW etl.genre_v
AS 
SELECT t.*, ((EXTRACT(epoch FROM updated_at)::float)::text || '-' || id)::text  combined_key
FROM content.genre t;


CREATE OR REPLACE VIEW etl.person_film_work_v
AS 
SELECT t.*, ((EXTRACT(epoch FROM updated_at)::float)::text || '-' || id)::text  combined_key
FROM content.person_film_work t;


CREATE OR REPLACE VIEW etl.genre_film_work_v
AS 
SELECT t.*, ((EXTRACT(epoch FROM updated_at)::float)::text || '-' || id)::text  combined_key
FROM content.genre_film_work t;


CREATE FUNCTION etl.get_film_work_by_person_key(p_combined_key TEXT, p_batch_size INTEGER) RETURNS TABLE ( 
		id uuid,
		title TEXT,
		description TEXT,
		creation_date DATE,
		rating FLOAT,
		type TEXT,
		created_at timestamp with time zone,
		updated_at timestamp with time zone,
		combined_key TEXT,
		max_in_combined_key TEXT 
		)
	AS $$
BEGIN
    RETURN QUERY 
	WITH ordered as (
SELECT DISTINCT 
fw.*, p.combined_key in_combined_key
FROM etl.film_work_v fw
JOIN content.person_film_work pfw ON fw.id = pfw.film_work_id
JOIN etl.person_v p ON p.id = pfw.person_id
WHERE
p.combined_key > p_combined_key
ORDER BY p.combined_key
LIMIT (p_batch_size)
)
,combined_key as (
SELECT max(in_combined_key)::text max_in_combined_key
FROM ordered t
)
SELECT t.id,
		t.title,
		t.description,
		t.creation_date,
		t.rating,
		t.type,
		t.created_at,
		t.updated_at,
		t.combined_key,
		combined_key.max_in_combined_key
FROM ordered t, combined_key
;
END; $$ LANGUAGE plpgsql STRICT;


CREATE FUNCTION etl.get_film_work_by_film_work_key(p_combined_key TEXT, p_batch_size INTEGER) RETURNS TABLE (
		id uuid,
		title TEXT,
		description TEXT,
		creation_date DATE,
		rating FLOAT,
		type TEXT,
		created_at timestamp with time zone,
		updated_at timestamp with time zone,
		combined_key TEXT,
		max_in_combined_key TEXT 		
		)
	AS $$
BEGIN
    RETURN QUERY 
	WITH ordered as (
SELECT DISTINCT 
fw.*, fw.combined_key in_combined_key
FROM etl.film_work_v fw
WHERE
fw.combined_key > p_combined_key
ORDER BY fw.combined_key
LIMIT (p_batch_size)
)
,combined_key as (
SELECT max(in_combined_key)::text max_in_combined_key
FROM ordered t
)
SELECT t.id,
		t.title,
		t.description,
		t.creation_date,
		t.rating,
		t.type,
		t.created_at,
		t.updated_at,
		t.combined_key,
		combined_key.max_in_combined_key
FROM ordered t, combined_key
;
END; $$ LANGUAGE plpgsql STRICT;


CREATE FUNCTION etl.get_film_work_by_genre_key(p_combined_key TEXT, p_batch_size INTEGER) RETURNS TABLE ( id uuid,
		title TEXT,
		description TEXT,
		creation_date DATE,
		rating FLOAT,
		type TEXT,
		created_at timestamp with time zone,
		updated_at timestamp with time zone,
		combined_key TEXT,
		max_in_combined_key TEXT 
		)
	AS $$
BEGIN
    RETURN QUERY 
	WITH ordered as (
SELECT DISTINCT 
fw.*, g.combined_key in_combined_key
FROM etl.film_work_v fw
JOIN content.genre_film_work gfw ON fw.id = gfw.film_work_id
JOIN etl.genre_v g ON g.id = gfw.genre_id
WHERE
g.combined_key > p_combined_key
ORDER BY g.combined_key
LIMIT (p_batch_size)
)
,combined_key as (
SELECT max(in_combined_key)::text max_in_combined_key
FROM ordered t
)
SELECT t.id,
		t.title,
		t.description,
		t.creation_date,
		t.rating,
		t.type,
		t.created_at,
		t.updated_at,
		t.combined_key,
		combined_key.max_in_combined_key
FROM ordered t, combined_key
;
END; $$ LANGUAGE plpgsql STRICT;


CREATE FUNCTION etl.get_film_work_by_person_film_work_key(p_combined_key TEXT, p_batch_size INTEGER) RETURNS TABLE ( 
		id uuid,
		title TEXT,
		description TEXT,
		creation_date DATE,
		rating FLOAT,
		type TEXT,
		created_at timestamp with time zone,
		updated_at timestamp with time zone,
		combined_key TEXT,
		max_in_combined_key TEXT 
		)
	AS $$
BEGIN
    RETURN QUERY 
	WITH ordered as (
SELECT DISTINCT 
fw.*, pfw.combined_key in_combined_key
FROM etl.film_work_v fw
JOIN etl.person_film_work_v pfw ON fw.id = pfw.film_work_id
WHERE
pfw.combined_key > p_combined_key
ORDER BY pfw.combined_key
LIMIT (p_batch_size)
)
,combined_key as (
SELECT max(in_combined_key)::text max_in_combined_key
FROM ordered t
)
SELECT t.id,
		t.title,
		t.description,
		t.creation_date,
		t.rating,
		t.type,
		t.created_at,
		t.updated_at,
		t.combined_key,
		combined_key.max_in_combined_key
FROM ordered t, combined_key
;
END; $$ LANGUAGE plpgsql STRICT;


CREATE FUNCTION etl.get_film_work_by_genre_film_work_key(p_combined_key TEXT, p_batch_size INTEGER) RETURNS TABLE ( id uuid,
		title TEXT,
		description TEXT,
		creation_date DATE,
		rating FLOAT,
		type TEXT,
		created_at timestamp with time zone,
		updated_at timestamp with time zone,
		combined_key TEXT,
		max_in_combined_key TEXT 
		)
	AS $$
BEGIN
    RETURN QUERY 
	WITH ordered as (
SELECT DISTINCT 
fw.*, gfw.combined_key in_combined_key
FROM etl.film_work_v fw
JOIN etl.genre_film_work_v gfw ON fw.id = gfw.film_work_id
WHERE
gfw.combined_key > p_combined_key
ORDER BY gfw.combined_key
LIMIT (p_batch_size)
)
,combined_key as (
SELECT max(in_combined_key)::text max_in_combined_key
FROM ordered t
)
SELECT t.id,
		t.title,
		t.description,
		t.creation_date,
		t.rating,
		t.type,
		t.created_at,
		t.updated_at,
		t.combined_key,
		combined_key.max_in_combined_key
FROM ordered t, combined_key
;
END; $$ LANGUAGE plpgsql STRICT;

