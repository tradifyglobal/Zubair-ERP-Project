-- Create user tradifyerp_user with password
CREATE USER tradifyerp_user WITH PASSWORD 'Tradify@PostgreSQL2024';

-- Create database tradifyerp_db
CREATE DATABASE tradifyerp_db OWNER tradifyerp_user;

-- Grant all privileges
GRANT ALL PRIVILEGES ON DATABASE tradifyerp_db TO tradifyerp_user;

-- Verify creation
SELECT usename FROM pg_user WHERE usename = 'tradifyerp_user';
SELECT datname FROM pg_database WHERE datname = 'tradifyerp_db';
