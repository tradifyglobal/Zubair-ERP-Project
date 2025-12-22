-- Terminate all connections to tradify database
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'tradify'
  AND pid <> pg_backend_pid();

-- Wait a moment and then rename
ALTER DATABASE tradify RENAME TO tradify_backup_inactive;

-- Verify
SELECT datname FROM pg_database WHERE datname LIKE 'tradify%' ORDER BY datname;
