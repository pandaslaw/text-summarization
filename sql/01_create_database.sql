-- Create database if it doesn't exist
SELECT 'CREATE DATABASE llm_reports'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'llm_reports')\gexec
