-- Database initialization script for local development
-- This script runs automatically when the PostgreSQL container starts

-- Create extensions (if needed)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create development database (already done by POSTGRES_DB, but keeping for reference)
-- CREATE DATABASE chatbot_dev;

-- Grant privileges (already handled by POSTGRES_USER setup)
-- GRANT ALL PRIVILEGES ON DATABASE chatbot_dev TO chatbot_user;

-- Log successful initialization
SELECT 'Database initialized successfully' as status;