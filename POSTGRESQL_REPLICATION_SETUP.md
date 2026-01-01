# PostgreSQL Streaming Replication Setup Guide

**Date**: December 23, 2025  
**Target**: PostgreSQL 16 Master-Standby Replication  
**Primary**: 192.168.20.11  
**Standby**: 192.168.20.21

---

## 📋 Prerequisites

### On Primary Server (192.168.20.11)
- PostgreSQL 16 installed and running
- Database: `tradifyerp_db` created
- User: `tradifyerp_user` with privileges
- Network connectivity to standby server
- SSH access to standby server

### On Standby Server (192.168.20.21)
- PostgreSQL 16 installed (same version)
- Network connectivity to primary server
- SSH access to primary server
- Same storage layout as primary
- Passwordless sudo configured

---

## 🚀 Step 1: Create Replication User (Primary Server)

```bash
# SSH to primary database server
ssh zubair@192.168.20.11

# Connect to PostgreSQL as superuser
sudo -u postgres psql

-- Create replication user
CREATE USER repuser WITH REPLICATION ENCRYPTED PASSWORD 'RepPassword2024!';

-- Grant replication permissions
ALTER USER repuser WITH SUPERUSER;

-- Verify
\du repuser

-- Exit psql
\q
```

---

## 🔧 Step 2: Configure Primary Server for Replication

### Edit PostgreSQL Configuration

```bash
sudo nano /etc/postgresql/16/main/postgresql.conf
```

Add/modify these settings:

```ini
# REPLICATION SETTINGS
wal_level = replica                    # Enable WAL archiving
max_wal_senders = 10                   # Max concurrent replicas
max_replication_slots = 10             # Reserve slots for replicas
wal_keep_size = '2GB'                  # Keep WAL segments
hot_standby = on                       # Allow read queries on standby
hot_standby_feedback = on              # Standby feedback to prevent conflicts
synchronous_commit = on                # Synchronous replication (recommended)
synchronous_standby_names = '*'        # All standbys must confirm

# ARCHIVING SETTINGS (Optional but recommended)
archive_mode = on
archive_command = 'test ! -f /var/lib/postgresql/16/main/archive/%f && cp %p /var/lib/postgresql/16/main/archive/%f'
archive_timeout = 300

# LOGGING
log_replication_commands = on
```

### Edit pg_hba.conf (Add Replication Connection)

```bash
sudo nano /etc/postgresql/16/main/pg_hba.conf
```

Add this line after existing entries:

```
# Replication connections
host    replication     repuser         192.168.20.21/32        scram-sha-256
host    replication     repuser         ::1/128                 scram-sha-256
```

### Create Archive Directory (Optional)

```bash
sudo mkdir -p /var/lib/postgresql/16/main/archive
sudo chown postgres:postgres /var/lib/postgresql/16/main/archive
sudo chmod 700 /var/lib/postgresql/16/main/archive
```

### Restart Primary PostgreSQL

```bash
sudo systemctl restart postgresql@16-main

# Verify replication settings
sudo -u postgres psql -c "SHOW wal_level; SHOW max_wal_senders; SHOW synchronous_commit;"
```

Expected output:
```
 wal_level | max_wal_senders | synchronous_commit
-----------+-----------------+-------------------
 replica   |              10 | on
```

---

## 📦 Step 3: Create Base Backup (Primary Server)

Create a backup of the primary database to seed the standby:

```bash
# SSH to primary
ssh zubair@192.168.20.11

# Create backup directory
sudo mkdir -p /var/lib/postgresql/backup
sudo chown postgres:postgres /var/lib/postgresql/backup

# Create base backup as postgres user
sudo -u postgres pg_basebackup \
    -h 192.168.20.11 \
    -D /var/lib/postgresql/backup \
    -U repuser \
    -v \
    -P \
    -W \
    -Fp \
    -R

# Enter repuser password: RepPassword2024!
# This creates a full backup and includes recovery configuration
```

The backup includes:
- Complete database data
- WAL files
- `standby.signal` file (to start as standby)
- `recovery.conf` (replication configuration)

Verify backup:
```bash
ls -lah /var/lib/postgresql/backup/
sudo cat /var/lib/postgresql/backup/recovery.conf
```

---

## 📤 Step 4: Transfer Backup to Standby Server

```bash
# From primary server
sudo chmod -R 755 /var/lib/postgresql/backup

# Transfer to standby
sudo rsync -avz --delete /var/lib/postgresql/backup/ \
    zubair@192.168.20.21:/var/lib/postgresql/backup/

# Or using scp (if rsync not available)
sudo tar -czf /tmp/backup.tar.gz /var/lib/postgresql/backup/
scp /tmp/backup.tar.gz zubair@192.168.20.21:/tmp/
```

---

## 🛠️ Step 5: Set Up Standby Server

### SSH to Standby Server

```bash
ssh zubair@192.168.20.21
```

### Configure PostgreSQL on Standby

Edit postgresql.conf:

```bash
sudo nano /etc/postgresql/16/main/postgresql.conf
```

Make sure standby has same settings as primary (especially `hot_standby = on`):

```ini
hot_standby = on
hot_standby_feedback = on
max_standby_streaming_delay = 30min
```

### Restore Backup to Data Directory

```bash
# Stop any running PostgreSQL
sudo systemctl stop postgresql@16-main

# Clear existing data directory
sudo rm -rf /var/lib/postgresql/16/main/*

# Copy backup to data directory
sudo cp -r /var/lib/postgresql/backup/* /var/lib/postgresql/16/main/

# Fix permissions
sudo chown -R postgres:postgres /var/lib/postgresql/16/main
sudo chmod 700 /var/lib/postgresql/16/main

# Verify standby.signal exists
sudo ls -la /var/lib/postgresql/16/main/standby.signal
sudo cat /var/lib/postgresql/16/main/recovery.conf
```

The recovery.conf should look like:

```conf
standby_mode = 'on'
primary_conninfo = 'host=192.168.20.11 port=5432 user=repuser password=RepPassword2024!'
```

If recovery.conf doesn't exist, create it:

```bash
sudo nano /var/lib/postgresql/16/main/recovery.conf
```

Add:
```
standby_mode = 'on'
primary_conninfo = 'host=192.168.20.11 port=5432 user=repuser password=RepPassword2024! application_name=standby1'
recovery_target_timeline = 'latest'
wal_retrieve_command = 'cp /var/lib/postgresql/wal_archive/%f "%p"'
```

### Start Standby PostgreSQL

```bash
sudo systemctl start postgresql@16-main

# Check status
sudo systemctl status postgresql@16-main

# View logs
sudo tail -50 /var/log/postgresql/postgresql-16-main.log
```

Expected in logs:
```
LOG:  entering standby mode
LOG:  started streaming WAL from primary at 0/3000000 on timeline 1
```

---

## ✅ Step 6: Verify Replication is Working

### On Primary Server (192.168.20.11)

```bash
sudo -u postgres psql

-- Check replication slots
SELECT slot_name, slot_type, active FROM pg_replication_slots;

-- Check connected replication clients
SELECT usename, application_name, state FROM pg_stat_replication;

-- Check replication lag
SELECT now() - pg_last_xact_replay_timestamp() AS replication_lag;

-- View WAL sender status
SELECT pid, usename, application_name, backend_start, state FROM pg_stat_replication;
```

Expected output shows replication client connected and streaming:
```
 usename |    application_name    |    state    | sync_state
---------+------------------------+-------------+----------
 repuser |    standby1            | streaming   | async
```

### On Standby Server (192.168.20.21)

```bash
sudo -u postgres psql

-- Check recovery status
SELECT pg_is_in_recovery();
-- Output: t (true) = standby mode

-- Check replication status
SELECT status FROM pg_stat_wal_receiver;
-- Output: streaming

-- View receiver info
SELECT * FROM pg_stat_wal_receiver;
```

Expected:
```
 pg_is_in_recovery
------------------
 t
```

---

## 🔄 Step 7: Test Failover Process

### Scenario 1: Test Promotion to Master

On standby server:

```bash
# Promote standby to master (don't do this yet, just test!)
sudo -u postgres pg_ctl promote -D /var/lib/postgresql/16/main

# OR using pg_ctlcluster
sudo pg_ctlcluster 16 main promote

# Check status (should now be master)
sudo -u postgres psql -c "SELECT pg_is_in_recovery();"
# Output: f (false) = master mode
```

**After promotion:**
- Standby becomes master and accepts writes
- Old master is now disconnected
- You can fail back when primary is repaired

### Scenario 2: Write Test (Before Failover)

Create test data on primary:

```bash
# On primary (192.168.20.11)
sudo -u postgres psql tradifyerp_db

CREATE TABLE replication_test (
    id SERIAL PRIMARY KEY,
    test_time TIMESTAMP DEFAULT NOW(),
    message TEXT
);

INSERT INTO replication_test (message) VALUES ('Replication test from primary');
INSERT INTO replication_test (message) VALUES ('Test 2 from primary');

SELECT * FROM replication_test;
```

Verify on standby:

```bash
# On standby (192.168.20.21)
sudo -u postgres psql tradifyerp_db

-- Query will work (read-only)
SELECT * FROM replication_test;
```

The test data should appear on standby within seconds!

---

## 📊 Monitoring Replication Health

### Check Replication Lag

```bash
# On primary
sudo -u postgres psql -c "SELECT now() - pg_last_xact_replay_timestamp() AS replication_lag;"
```

Healthy: < 1 second  
Warning: 1-5 seconds  
Critical: > 5 seconds

### Check WAL Sender Status

```bash
# On primary
sudo -u postgres psql -c "SELECT pid, usename, application_name, state, sync_state, flush_lsn FROM pg_stat_replication;"
```

Should show:
- `state` = `streaming`
- `sync_state` = `sync` (if synchronous replication configured)

### Monitor Logs

```bash
# Real-time log monitoring
sudo tail -f /var/log/postgresql/postgresql-16-main.log
```

### Check Available Disk Space

```bash
# Both servers must have enough disk space for WAL files
df -h /var/lib/postgresql/

# Typical WAL file size: 16MB per file
# Monitor WAL archive directory
du -sh /var/lib/postgresql/16/main/pg_wal/
```

---

## 🔐 Production Configuration

### Enable SSL for Replication (Recommended)

```bash
# Generate SSL certificates
sudo -u postgres openssl req -x509 -newkey rsa:2048 -keyout /var/lib/postgresql/16/main/server.key -out /var/lib/postgresql/16/main/server.crt -days 365 -nodes

# Fix permissions
sudo chmod 600 /var/lib/postgresql/16/main/server.key
sudo chown postgres:postgres /var/lib/postgresql/16/main/server.*

# Edit postgresql.conf
ssl = on
ssl_cert_file = 'server.crt'
ssl_key_file = 'server.key'

# Restart PostgreSQL
sudo systemctl restart postgresql@16-main
```

Update recovery.conf to use SSL:

```
primary_conninfo = 'host=192.168.20.11 port=5432 user=repuser password=RepPassword2024! sslmode=require'
```

### Synchronous Replication (Zero Data Loss)

```bash
# Edit postgresql.conf on primary
synchronous_commit = remote_apply    # Wait for apply on standby
synchronous_standby_names = '*'      # Require all standbys to confirm
```

This ensures:
- Every transaction is replicated before confirmed to application
- Zero data loss on failover
- Slight performance impact (transactions wait for replication)

---

## ⚠️ Troubleshooting

### Replication Not Starting

**Error**: "could not open file /var/lib/postgresql/16/main/recovery.conf"

**Solution**:
```bash
sudo -u postgres touch /var/lib/postgresql/16/main/standby.signal
sudo systemctl restart postgresql@16-main
```

### Replication Lag High

**Issue**: `replication_lag` shows > 5 seconds

**Solutions**:
1. Check network bandwidth between servers
2. Reduce `synchronous_commit` to `on` (less strict)
3. Increase `max_wal_senders` on primary
4. Check disk I/O on both servers

### Standby Cannot Connect to Primary

**Error**: "could not connect to primary"

**Solutions**:
1. Check network: `ping 192.168.20.11`
2. Check pg_hba.conf on primary allows replication
3. Verify repuser password correct in recovery.conf
4. Check firewall allows port 5432

### Standby Disk Full

**Error**: "WAL file segmentation error"

**Solution**:
```bash
# Clean old WAL files
sudo -u postgres pg_archivecleanup -d /var/lib/postgresql/16/main/pg_wal/ $(sudo -u postgres psql -t -c "SELECT pg_wal_lsn_diff(pg_current_wal_lsn(), '0/0')::text;")

# Or increase disk space
```

---

## 🎯 Next Steps

1. ✓ Replication is now working
2. → Set up automatic monitoring (next guide)
3. → Configure HAProxy load balancer (next guide)
4. → Test failover procedures (guide)
5. → Monitor replication in production

---

*PostgreSQL Streaming Replication Setup*  
*For: Zubair ERP System*  
*Date: December 23, 2025*
