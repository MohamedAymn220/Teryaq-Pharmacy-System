-- TeryaqPharma Database Initialization Script
-- This script runs automatically when the PostgreSQL container starts for the first time

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For fuzzy text search

-- Create a function to check database health
CREATE OR REPLACE FUNCTION check_db_health()
RETURNS TABLE (status TEXT, timestamp TIMESTAMP) AS $$
BEGIN
    RETURN QUERY SELECT 'healthy'::TEXT, NOW();
END;
$$ LANGUAGE plpgsql;

-- Grant permissions (adjust as needed)
GRANT CONNECT ON DATABASE teryaq_db TO teryaq_user;
GRANT USAGE ON SCHEMA public TO teryaq_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO teryaq_user;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT ON TABLES TO teryaq_user;

-- Create an audit log table (optional - for tracking changes)
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    record_id INTEGER NOT NULL,
    action VARCHAR(20) NOT NULL,  -- INSERT, UPDATE, DELETE
    old_data JSONB,
    new_data JSONB,
    changed_by VARCHAR(100),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for audit log queries
CREATE INDEX IF NOT EXISTS idx_audit_log_table_record 
ON audit_log(table_name, record_id);

CREATE INDEX IF NOT EXISTS idx_audit_log_changed_at 
ON audit_log(changed_at DESC);

-- Log the initialization
INSERT INTO audit_log (table_name, record_id, action, changed_by)
VALUES ('system', 0, 'INIT', 'db_init.sql');