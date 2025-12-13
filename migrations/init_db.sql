-- ============================================================================
-- Machine Metadata Database Schema
-- Initial schema definition for GONSTERS Backend
-- ============================================================================


-- Create extension to generate UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


-- ============================================================================
-- Main Table: machine_metadata
-- ============================================================================
-- This table stores industrial machine metadata including
-- location, sensor type, and operational status.
-- ============================================================================


CREATE TABLE IF NOT EXISTS machine_metadata (
    -- Primary Key: UUID for unique machine identification
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    
    -- Machine name (e.g., "CNC-Machine-01", "Compressor-A1")
    name VARCHAR(255) NOT NULL,

    
    -- Physical location (e.g., "Factory Floor 1", "Building A - Zone 3")
    location VARCHAR(500) NOT NULL,

    
    -- Installed sensor type (e.g., "Temperature", "Pressure", "Vibration")
    sensor_type VARCHAR(100) NOT NULL,

    
    -- Current operational status
    -- Values: 'active', 'inactive', 'maintenance', 'error'
    status VARCHAR(50) NOT NULL DEFAULT 'active',

    
    -- Timestamp for audit trail
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_status CHECK (status IN ('active', 'inactive', 'maintenance', 'error'))

);

-- ============================================================================
-- Indexes for Query Optimization
-- ============================================================================


-- Index on name for machine lookup
CREATE INDEX idx_machine_name ON machine_metadata(name);


-- Index on location for location-based queries
CREATE INDEX idx_machine_location ON machine_metadata(location);


-- Index on sensor_type for sensor type filtering
CREATE INDEX idx_machine_sensor_type ON machine_metadata(sensor_type);


-- Index on status for active/inactive machine filtering
CREATE INDEX idx_machine_status ON machine_metadata(status);


-- Composite index for common query patterns (location + status)
CREATE INDEX idx_machine_location_status ON machine_metadata(location, status);


-- Index on created_at for time-based queries
CREATE INDEX idx_machine_created_at ON machine_metadata(created_at);


-- ============================================================================
-- Partitioning Strategy for Historical Analytics
-- ============================================================================
-- For large-scale deployments with thousands of machines, we can implement
-- partitioning. Below is an example of range partitioning based on created_at.
-- Disabled by default (commented), can be enabled for production.
-- ============================================================================


/*
-- Drop old table and recreate with partitioning
DROP TABLE IF EXISTS machine_metadata;


CREATE TABLE machine_metadata (
    id UUID DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    location VARCHAR(500) NOT NULL,
    sensor_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_status CHECK (status IN ('active', 'inactive', 'maintenance', 'error'))
) PARTITION BY RANGE (created_at);

-- Create partitions for each year
CREATE TABLE machine_metadata_2024 PARTITION OF machine_metadata

    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

CREATE TABLE machine_metadata_2025 PARTITION OF machine_metadata
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

-- Indexes on partitioned table
CREATE INDEX idx_machine_name ON machine_metadata(name);

CREATE INDEX idx_machine_location_status ON machine_metadata(location, status);
*/

-- ============================================================================
-- Trigger to automatically update updated_at timestamp
-- ============================================================================


CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_machine_metadata_updated_at
    BEFORE UPDATE ON machine_metadata
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Sample Data for Testing
-- ============================================================================


INSERT INTO machine_metadata (name, location, sensor_type, status) VALUES
    ('CNC-Machine-01', 'Factory Floor 1 - Zone A', 'Temperature', 'active'),
    ('CNC-Machine-02', 'Factory Floor 1 - Zone A', 'Pressure', 'active'),
    ('Compressor-A1', 'Factory Floor 2 - Zone B', 'Pressure', 'active'),
    ('Compressor-A2', 'Factory Floor 2 - Zone B', 'Temperature', 'maintenance'),
    ('Conveyor-Belt-01', 'Warehouse - Section C', 'Speed', 'active'),
    ('Hydraulic-Press-01', 'Factory Floor 1 - Zone C', 'Pressure', 'active'),
    ('Cooling-Unit-01', 'Factory Floor 3 - Zone D', 'Temperature', 'inactive');

-- ============================================================================
-- Verification Queries
-- ============================================================================


-- Verify table creation
SELECT table_name, column_name, data_type 
 
FROM information_schema.columns 
WHERE table_name = 'machine_metadata'
ORDER BY ordinal_position;

-- Verify indexes
SELECT indexname, indexdef 
 
FROM pg_indexes 
WHERE tablename = 'machine_metadata';

-- Count total records
SELECT COUNT(*) as total_machines FROM machine_metadata;


-- Example query: Active machines by location
SELECT location, COUNT(*) as active_machines

FROM machine_metadata
WHERE status = 'active'
GROUP BY location
ORDER BY active_machines DESC;
