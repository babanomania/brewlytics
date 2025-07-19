DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'metabase') THEN
        CREATE DATABASE metabase;
    END IF;
END$$;
