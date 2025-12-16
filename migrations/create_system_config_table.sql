-- Migration: Create system_config table
-- Date: 2025-12-16
-- Description: Add persistent configuration storage table for system settings

CREATE TABLE IF NOT EXISTS system_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    setting_name VARCHAR(255) NOT NULL UNIQUE,
    setting_value TEXT NOT NULL,
    description TEXT,
    updated_by VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Create index on setting_name for faster lookups
CREATE INDEX IF NOT EXISTS idx_system_config_setting_name ON system_config(setting_name);

-- Add comment to table
COMMENT ON TABLE system_config IS 'Stores system configuration settings in key-value format';
COMMENT ON COLUMN system_config.setting_name IS 'Unique identifier for the configuration setting';
COMMENT ON COLUMN system_config.setting_value IS 'Value of the configuration setting (stored as text)';
COMMENT ON COLUMN system_config.description IS 'Human-readable description of the setting';
COMMENT ON COLUMN system_config.updated_by IS 'Username of the user who last updated this setting';

-- Insert default configuration values
INSERT INTO system_config (setting_name, setting_value, description, updated_by)
VALUES 
    ('max_temperature_threshold', '80.0', 'Maximum temperature threshold in Celsius for alert triggering', 'system'),
    ('min_temperature_threshold', '50.0', 'Minimum temperature threshold in Celsius for alert triggering', 'system'),
    ('max_pressure_threshold', '150.0', 'Maximum pressure threshold in PSI for alert triggering', 'system'),
    ('alert_email', 'alerts@factory.com', 'Email address for system alerts', 'system'),
    ('data_retention_days', '365', 'Number of days to retain sensor data', 'system')
ON CONFLICT (setting_name) DO NOTHING;

-- Add trigger to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_system_config_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_system_config_updated_at
    BEFORE UPDATE ON system_config
    FOR EACH ROW
    EXECUTE FUNCTION update_system_config_timestamp();
