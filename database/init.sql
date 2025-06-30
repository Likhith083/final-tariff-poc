-- Tariff Management Chatbot Database Initialization
-- PostgreSQL with TimescaleDB and pgvector extensions

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "timescaledb";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Create database schema
CREATE SCHEMA IF NOT EXISTS tariff_chatbot;

-- Set search path
SET search_path TO tariff_chatbot, public;

-- Countries table
CREATE TABLE IF NOT EXISTS countries (
    country_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    iso_code VARCHAR(2) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- HTS Codes table
CREATE TABLE IF NOT EXISTS hts_codes (
    hts_code_id SERIAL PRIMARY KEY,
    code VARCHAR(10) UNIQUE NOT NULL,
    description TEXT NOT NULL,
    chapter VARCHAR(2),
    heading VARCHAR(4),
    subheading VARCHAR(4),
    statistical_suffix VARCHAR(2),
    level INTEGER,
    parent_code VARCHAR(10),
    last_updated_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tariff Rates table
CREATE TABLE IF NOT EXISTS tariff_rates (
    tariff_rate_id SERIAL PRIMARY KEY,
    hts_code_id INTEGER NOT NULL REFERENCES hts_codes(hts_code_id),
    country_of_origin_id INTEGER NOT NULL REFERENCES countries(country_id),
    country_of_import_id INTEGER NOT NULL REFERENCES countries(country_id),
    effective_date DATE NOT NULL,
    expiry_date DATE,
    rate_percentage NUMERIC(5,2),
    rate_amount NUMERIC(10,4),
    currency VARCHAR(3) DEFAULT 'USD',
    type VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Products table
CREATE TABLE IF NOT EXISTS products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    material_composition_text TEXT,
    inferred_material_composition JSONB,
    current_hts_code_id INTEGER REFERENCES hts_codes(hts_code_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Materials table
CREATE TABLE IF NOT EXISTS materials (
    material_id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    properties_json JSONB,
    hts_code_id_suggestion INTEGER REFERENCES hts_codes(hts_code_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- HTS Code Embeddings table (for vector search)
CREATE TABLE IF NOT EXISTS hts_code_embeddings (
    embedding_id SERIAL PRIMARY KEY,
    hts_code_id INTEGER UNIQUE NOT NULL REFERENCES hts_codes(hts_code_id),
    embedding_vector vector(1536),
    source_text TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User Subscriptions table
CREATE TABLE IF NOT EXISTS user_subscriptions (
    subscription_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    hts_code_id INTEGER NOT NULL REFERENCES hts_codes(hts_code_id),
    country_of_origin_id INTEGER NOT NULL REFERENCES countries(country_id),
    country_of_import_id INTEGER NOT NULL REFERENCES countries(country_id),
    notification_frequency VARCHAR(20) DEFAULT 'daily',
    last_notified_date TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Chat Sessions table
CREATE TABLE IF NOT EXISTS chat_sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Chat Messages table
CREATE TABLE IF NOT EXISTS chat_messages (
    message_id SERIAL PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES chat_sessions(session_id),
    content TEXT NOT NULL,
    role VARCHAR(20) NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_countries_iso_code ON countries(iso_code);
CREATE INDEX IF NOT EXISTS idx_hts_codes_code ON hts_codes(code);
CREATE INDEX IF NOT EXISTS idx_hts_codes_hierarchy ON hts_codes(chapter, heading, subheading);
CREATE INDEX IF NOT EXISTS idx_hts_codes_level ON hts_codes(level);
CREATE INDEX IF NOT EXISTS idx_hts_codes_parent ON hts_codes(parent_code);
CREATE INDEX IF NOT EXISTS idx_tariff_rates_effective ON tariff_rates(effective_date);
CREATE INDEX IF NOT EXISTS idx_tariff_rates_country_pair ON tariff_rates(country_of_origin_id, country_of_import_id);
CREATE INDEX IF NOT EXISTS idx_tariff_rates_hts_country ON tariff_rates(hts_code_id, country_of_origin_id, country_of_import_id);
CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);
CREATE INDEX IF NOT EXISTS idx_materials_name ON materials(name);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_active ON user_subscriptions(is_active);
CREATE INDEX IF NOT EXISTS idx_chat_messages_session ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_role ON chat_messages(role);

-- Create vector index for embeddings
CREATE INDEX IF NOT EXISTS idx_hts_embeddings_vector ON hts_code_embeddings USING ivfflat (embedding_vector vector_cosine_ops) WITH (lists = 100);

-- Convert tariff_rates to TimescaleDB hypertable for time-series data
SELECT create_hypertable('tariff_rates', 'effective_date', if_not_exists => TRUE);

-- Insert sample data
INSERT INTO countries (name, iso_code) VALUES 
    ('United States', 'US'),
    ('China', 'CN'),
    ('Canada', 'CA'),
    ('Mexico', 'MX'),
    ('Germany', 'DE'),
    ('Japan', 'JP'),
    ('United Kingdom', 'GB'),
    ('France', 'FR'),
    ('Italy', 'IT'),
    ('South Korea', 'KR')
ON CONFLICT (iso_code) DO NOTHING;

-- Insert sample HTS codes
INSERT INTO hts_codes (code, description, chapter, heading, subheading, level) VALUES 
    ('8471.30.01', 'Portable automatic data processing machines', '84', '8471', '30', 4),
    ('8517.13.00', 'Smartphones', '85', '8517', '13', 4),
    ('9503.00.00', 'Other toys', '95', '9503', '00', 4),
    ('6104.43.20', 'Women''s dresses of synthetic fibers', '61', '6104', '43', 4),
    ('8528.72.72', 'Color television receivers', '85', '8528', '72', 4)
ON CONFLICT (code) DO NOTHING;

-- Insert sample tariff rates
INSERT INTO tariff_rates (hts_code_id, country_of_origin_id, country_of_import_id, effective_date, rate_percentage, type) VALUES 
    (1, 2, 1, '2024-01-01', 25.0, 'Section 301'),
    (2, 2, 1, '2024-01-01', 0.0, 'MFN'),
    (3, 2, 1, '2024-01-01', 0.0, 'MFN'),
    (4, 2, 1, '2024-01-01', 16.0, 'MFN'),
    (5, 2, 1, '2024-01-01', 5.0, 'MFN')
ON CONFLICT DO NOTHING;

-- Create default admin user (password: admin123)
INSERT INTO users (username, email, password_hash, role) VALUES 
    ('admin', 'admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5u.G', 'admin')
ON CONFLICT (username) DO NOTHING;

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_chat_sessions_updated_at BEFORE UPDATE ON chat_sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA tariff_chatbot TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA tariff_chatbot TO postgres;

-- Create views for common queries
CREATE OR REPLACE VIEW tariff_summary AS
SELECT 
    hc.code as hts_code,
    hc.description as hts_description,
    co.name as origin_country,
    ci.name as import_country,
    tr.rate_percentage,
    tr.effective_date,
    tr.type
FROM tariff_rates tr
JOIN hts_codes hc ON tr.hts_code_id = hc.hts_code_id
JOIN countries co ON tr.country_of_origin_id = co.country_id
JOIN countries ci ON tr.country_of_import_id = ci.country_id
WHERE tr.effective_date <= CURRENT_DATE
AND (tr.expiry_date IS NULL OR tr.expiry_date >= CURRENT_DATE);

-- Create materialized view for performance
CREATE MATERIALIZED VIEW IF NOT EXISTS hts_code_summary AS
SELECT 
    hc.hts_code_id,
    hc.code,
    hc.description,
    hc.chapter,
    hc.heading,
    hc.subheading,
    hc.level,
    COUNT(tr.tariff_rate_id) as tariff_rate_count,
    AVG(tr.rate_percentage) as avg_rate_percentage
FROM hts_codes hc
LEFT JOIN tariff_rates tr ON hc.hts_code_id = tr.hts_code_id
GROUP BY hc.hts_code_id, hc.code, hc.description, hc.chapter, hc.heading, hc.subheading, hc.level;

-- Create index on materialized view
CREATE UNIQUE INDEX IF NOT EXISTS idx_hts_code_summary_code ON hts_code_summary(code);

-- Refresh materialized view
REFRESH MATERIALIZED VIEW hts_code_summary; 