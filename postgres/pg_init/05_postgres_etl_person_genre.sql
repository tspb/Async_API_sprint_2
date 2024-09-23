\c movies_database app;

-- 4 sprint

-- DROP FUNCTION etl.get_person_by_person_key;
CREATE OR REPLACE FUNCTION etl.get_person_by_person_key(p_combined_key TEXT, p_batch_size INTEGER) RETURNS TABLE ( 
		id uuid,
		full_name TEXT,
		created_at timestamp with time zone,
		updated_at timestamp with time zone,
		gender text,
		combined_key TEXT,
		max_in_combined_key TEXT 
		)
	AS $$
BEGIN
    RETURN QUERY 
	WITH ordered as (
SELECT DISTINCT 
p.*, p.combined_key  in_combined_key
FROM etl.person_v p
WHERE
p.combined_key > p_combined_key
ORDER BY p.combined_key
LIMIT (p_batch_size)
)
,combined_key as (
SELECT max(in_combined_key)::text max_in_combined_key
FROM ordered t
)
SELECT  t.id,
		t.full_name,
		t.created_at,
		t.updated_at,
		t.gender,
		t.combined_key,
		combined_key.max_in_combined_key
FROM ordered t, combined_key
;
END; $$ LANGUAGE plpgsql STRICT;

-- DROP FUNCTION etl.get_genre_by_genre_key;
CREATE OR REPLACE FUNCTION etl.get_genre_by_genre_key(p_combined_key TEXT, p_batch_size INTEGER) RETURNS TABLE ( 
		id uuid,
		name TEXT,
		description TEXT,
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
g.*, g.combined_key  in_combined_key
FROM etl.genre_v g
WHERE
g.combined_key > p_combined_key
ORDER BY g.combined_key
LIMIT (p_batch_size)
)
,combined_key as (
SELECT max(in_combined_key)::text max_in_combined_key
FROM ordered t
)
SELECT  t.id,
		t.name,
		t.description,
		t.created_at,
		t.updated_at,
		t.combined_key,
		combined_key.max_in_combined_key
FROM ordered t, combined_key
;
END; $$ LANGUAGE plpgsql STRICT;

