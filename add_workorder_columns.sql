-- Add missing columns to maintenance_work_order table
ALTER TABLE maintenance_work_order ADD COLUMN IF NOT EXISTS completion_date DATE NULL;
ALTER TABLE maintenance_work_order ADD COLUMN IF NOT EXISTS is_posted_to_gl BOOLEAN DEFAULT FALSE NOT NULL;
