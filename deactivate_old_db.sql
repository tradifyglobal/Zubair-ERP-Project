-- Rename the old tradify database to indicate it's inactive/backup
-- First, create a note in a comments table or log

-- Option 1: Rename the database
ALTER DATABASE tradify RENAME TO tradify_backup_inactive;

-- Verify the rename
SELECT datname FROM pg_database WHERE datname LIKE 'tradify%' ORDER BY datname;
