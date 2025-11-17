# Automated Depreciation Scheduler

## Overview

The depreciation scheduler automatically runs depreciation generation at scheduled times without manual intervention. It runs as a background daemon thread in your Django process.

## Quick Start

### Start Scheduler
```bash
python manage.py depreciation_scheduler --start
```

**Output:**
```
✅ Depreciation scheduler started successfully

📅 Scheduled Time: 02:00
⏭️  Next Run: 2025-11-17T02:00:00+00:00
```

### Check Status
```bash
python manage.py depreciation_scheduler --status
```

**Output:**
```
============================================================
DEPRECIATION SCHEDULER STATUS
============================================================

🔄 Running: YES
✅ Enabled: YES
📅 Scheduled Time: 02:00 daily
⏭️  Next Run: 2025-11-17T02:00:00+00:00
⏱️  Last Run: 2025-11-17T02:00:15.123456
📝 Created: 2025-11-16T09:42:15.262424

============================================================
```

### Run Immediately
```bash
python manage.py depreciation_scheduler --run-now
```

### Stop Scheduler
```bash
python manage.py depreciation_scheduler --stop
```

---

## Management Commands

### Start Scheduler
```bash
python manage.py depreciation_scheduler --start
```
- Starts the scheduler in background
- Runs daily at 02:00 (2 AM)
- Creates config file for persistence
- Thread runs as daemon (stops when Django stops)

### Stop Scheduler
```bash
python manage.py depreciation_scheduler --stop
```
- Gracefully stops the scheduler thread
- Saves current state
- Can be restarted later

### Check Status
```bash
python manage.py depreciation_scheduler --status
```
- Shows running state (YES/NO)
- Shows enabled state
- Displays scheduled time
- Shows next scheduled run
- Shows last run time
- Displays last 10 log entries

### Run Now
```bash
python manage.py depreciation_scheduler --run-now
```
- Runs depreciation immediately (doesn't wait for scheduled time)
- Useful for testing or catching up

### Set Run Time
```bash
python manage.py depreciation_scheduler --time 23:30
```
- Changes daily run time
- Format: HH:MM (24-hour)
- Example: `02:00`, `14:30`, `23:59`

### Disable Scheduler
```bash
python manage.py depreciation_scheduler --disable
```
- Stops the scheduler from running
- Keeps configuration for later
- Can be re-enabled

### Enable Scheduler
```bash
python manage.py depreciation_scheduler --enable
```
- Re-enables the scheduler
- Uses previous configuration

---

## Configuration

### Default Configuration
```json
{
  "is_running": false,
  "run_time": "02:00",
  "last_run": null,
  "next_run": null,
  "enabled": true,
  "created_at": "2025-11-16T09:42:15.262424",
  "auto_start": true
}
```

### Config Location
```
g:\TradifyERP\depreciation_scheduler.json
```

### Config Fields

| Field | Type | Description |
|-------|------|-------------|
| `is_running` | boolean | Current running state |
| `run_time` | string | Daily run time (HH:MM format) |
| `last_run` | string/null | ISO timestamp of last run |
| `next_run` | string/null | ISO timestamp of next scheduled run |
| `enabled` | boolean | Whether scheduler is enabled |
| `created_at` | string | When scheduler was created |
| `auto_start` | boolean | Auto-start on Django startup |

---

## Logging

### Log Location
```
g:\TradifyERP\depreciation_scheduler.log
```

### Log Format
```
[2025-11-17T02:00:15.123456] ✅ Depreciation generated successfully
[2025-11-17T02:00:15.124789] Processing entity: Tradify ERP Corporation
[2025-11-17T02:00:15.125000] ✓ Created depreciation entry for Office Computer: 83.33
```

### View Last 10 Logs
```bash
python manage.py depreciation_scheduler --status
```
Shows recent logs in the status output.

---

## Startup Methods

### Method 1: Manual Start Each Time
```bash
python manage.py depreciation_scheduler --start
```
Run before starting the server.

### Method 2: Batch Script (Windows)
Use the provided `START_SERVER.bat`:
```bash
START_SERVER.bat
```

This will:
1. Start depreciation scheduler
2. Start Django server
3. Both run together

### Method 3: Auto-Start (Development)
In your development setup, create a startup sequence:

```bash
#!/bin/bash
# Linux/Mac startup script

cd g:/TradifyERP/TradifyERP

# Start scheduler in background
python manage.py depreciation_scheduler --start &

# Start server
python manage.py runserver 0.0.0.0:8000
```

### Method 4: Production (Gunicorn + Systemd)
See "Production Deployment" section below.

---

## How It Works

### Architecture
```
Django Server (Main Process)
    │
    └─→ Depreciation Scheduler (Background Thread)
            │
            ├─→ Checks time every 30 seconds
            ├─→ At scheduled time, runs: python manage.py generate_depreciation
            ├─→ Logs results
            └─→ Calculates next run time
```

### Execution Flow
1. **Scheduler starts** → Daemon thread begins
2. **Check loop runs** → Every 30 seconds checks if time matches
3. **Time matches** → Runs depreciation command once per day
4. **Process completes** → Updates last_run timestamp
5. **Calculates next** → Sets next_run for tomorrow
6. **Logs event** → Writes to depreciation_scheduler.log

### Schedule Details
- **Frequency**: Daily (once per day)
- **Default time**: 02:00 (2 AM)
- **Check interval**: Every 30 seconds
- **Timezone**: Uses Django's timezone setting (UTC by default)

---

## Examples

### Example 1: Daily at 2 AM (Default)
```bash
# Start with default settings
python manage.py depreciation_scheduler --start

# Output:
# 📅 Scheduled Time: 02:00
# ⏭️  Next Run: 2025-11-17T02:00:00+00:00
```

### Example 2: Daily at 11 PM
```bash
# Change to 11 PM
python manage.py depreciation_scheduler --time 23:00
python manage.py depreciation_scheduler --start

# Output:
# 📅 Scheduled Time: 23:00
# ⏭️  Next Run: 2025-11-16T23:00:00+00:00
```

### Example 3: Test Run
```bash
# Run immediately without waiting for scheduled time
python manage.py depreciation_scheduler --run-now

# Output:
# 🚀 Running depreciation now...
# Processing entity: Tradify ERP Corporation
# ✓ Created depreciation entry for Office Computer: 83.33
# ✅ Depreciation generated successfully
```

### Example 4: Monitor Execution
```bash
# Start in one terminal
python manage.py depreciation_scheduler --start

# In another terminal, monitor status
# Run this every 30 seconds to watch
python manage.py depreciation_scheduler --status
```

---

## Troubleshooting

### Problem: Scheduler not running after Django restart
**Solution**: The scheduler only runs while Django is running. Restart Django:
```bash
python manage.py depreciation_scheduler --start
python manage.py runserver 0.0.0.0:8000
```

### Problem: Depreciation not running at scheduled time
**Solution 1**: Check if scheduler is enabled:
```bash
python manage.py depreciation_scheduler --status
# Look for "✅ Enabled: YES"
```

**Solution 2**: Check if time is set correctly:
```bash
python manage.py depreciation_scheduler --status
# Look for "📅 Scheduled Time: HH:MM"
```

**Solution 3**: Check logs for errors:
```bash
cat g:\TradifyERP\depreciation_scheduler.log
```

### Problem: "Scheduler is already running"
**Solution**: Only one instance can run per Django process. Either:
1. Don't start it twice, or
2. Stop it first: `python manage.py depreciation_scheduler --stop`

### Problem: No depreciation entries created
**Possible causes**:
1. No active fixed assets exist
2. Assets purchased after run date (skipped by design)
3. Assets already have depreciation this month

**Debug**: Run manually:
```bash
python manage.py depreciation_scheduler --run-now
```

### Problem: Permission denied on config file
**Solution**: Ensure write permissions in `g:\TradifyERP\` directory

---

## Production Deployment

### Option 1: Systemd Service (Linux)
Create `/etc/systemd/system/tradify-depreciation.service`:

```ini
[Unit]
Description=TradifyERP Depreciation Scheduler
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/TradifyERP/TradifyERP
ExecStart=/path/to/venv/bin/python manage.py depreciation_scheduler --start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Start:
```bash
sudo systemctl enable tradify-depreciation
sudo systemctl start tradify-depreciation
```

### Option 2: Supervisor (Any Platform)
Create `/etc/supervisor/conf.d/tradify-depreciation.conf`:

```ini
[program:tradify-depreciation]
command=/path/to/venv/bin/python /path/to/TradifyERP/TradifyERP/manage.py depreciation_scheduler --start
directory=/path/to/TradifyERP/TradifyERP
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/tradify-depreciation.err.log
stdout_logfile=/var/log/tradify-depreciation.out.log
```

### Option 3: Docker
Add to Dockerfile or docker-compose.yml:

```yaml
version: '3'
services:
  tradify:
    build: .
    command: >
      sh -c "python manage.py depreciation_scheduler --start &
             python manage.py runserver 0.0.0.0:8000"
```

---

## Monitoring & Maintenance

### Weekly Check
```bash
python manage.py depreciation_scheduler --status
```

Verify:
- ✅ Running: YES
- ✅ Enabled: YES
- ✅ Recent logs showing successful runs

### Monthly Review
```bash
cat g:\TradifyERP\depreciation_scheduler.log | tail -50
```

Check for:
- Successful depreciation runs
- No error messages
- Proper timestamps

### Maintenance Commands

**Reset Configuration:**
```bash
python manage.py depreciation_scheduler --stop
# Delete file: g:\TradifyERP\depreciation_scheduler.json
python manage.py depreciation_scheduler --start
```

**Clear Logs:**
```bash
# Backup first
copy g:\TradifyERP\depreciation_scheduler.log g:\TradifyERP\depreciation_scheduler.log.backup

# Delete log
del g:\TradifyERP\depreciation_scheduler.log
```

---

## Architecture & Design

### Why Background Thread?
- ✅ No external dependencies (no Django Q, Celery, APScheduler)
- ✅ Simple to deploy
- ✅ Lightweight and fast
- ✅ Works with development server

### Limitations
- ⚠️ Stops when Django stops
- ⚠️ Only runs on one server (not distributed)
- ⚠️ Relies on Django process being up

### For Production Alternatives
If you need:
- **Distributed scheduling**: Use Celery + Redis
- **More features**: Use Django Q + background job system
- **High reliability**: Use external scheduler (cron, systemd)

---

## Reference

### Config File Format
```json
{
  "is_running": false,
  "run_time": "02:00",
  "last_run": "2025-11-17T02:00:15.123456",
  "next_run": "2025-11-18T02:00:00",
  "enabled": true,
  "created_at": "2025-11-16T09:42:15.262424",
  "auto_start": true
}
```

### Log File Format
```
[ISO_TIMESTAMP] [RESULT] MESSAGE
[2025-11-17T02:00:15.123456] ✅ Depreciation generated successfully
[2025-11-17T02:00:15.123456] Processing entity: Tradify ERP Corporation
[2025-11-17T02:00:15.123456] ✓ Created depreciation entry for Office Computer: 83.33
```

---

## Summary

✅ **Set up automated depreciation in 2 commands:**

```bash
python manage.py depreciation_scheduler --start
python manage.py runserver 0.0.0.0:8000
```

**Or use the batch script:**
```
START_SERVER.bat
```

That's it! Depreciation will run automatically every day at 2 AM.
