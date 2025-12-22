# TradifyERP Deployment Guide - New Servers

**Date:** December 13, 2025

## Infrastructure Overview

```
┌─────────────────────────────────────────────────────────┐
│ Application Server: 192.168.20.10                        │
│ - Ubuntu 24.04 LTS                                      │
│ - Django 5.2.9                                          │
│ - Gunicorn 23.0.0                                       │
│ - Nginx 1.24.0                                          │
│ - Python 3.12.3                                         │
│ - User: zubair                                          │
│ - Root password: erp                                    │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Database Server: 192.168.20.11                           │
│ - Ubuntu 24.04 LTS                                      │
│ - PostgreSQL 16.11                                      │
│ - User: zubair                                          │
│ - Root password: sql                                    │
│ - DB User: zubair                                       │
│ - DB: tradify                                           │
└─────────────────────────────────────────────────────────┘
```

## Deployment Checklist

### Phase 1: Database Server Setup (192.168.20.11)
- [ ] Install PostgreSQL 16
- [ ] Create database 'tradify'
- [ ] Create database user 'zubair'
- [ ] Configure PostgreSQL for remote connections
- [ ] Import data from prod_data_complete_backup.json

### Phase 2: Application Server Setup (192.168.20.10)
- [ ] Install Python 3.12
- [ ] Install system dependencies
- [ ] Clone/copy Django application
- [ ] Install Python requirements
- [ ] Configure settings.py for remote PostgreSQL
- [ ] Run migrations
- [ ] Collect static files
- [ ] Configure Gunicorn
- [ ] Configure Nginx

### Phase 3: Integration & Testing
- [ ] Test database connection from app server to db server
- [ ] Test Django admin
- [ ] Test dashboard
- [ ] Test all modules
- [ ] Verify UI theme (Minia + light green)
- [ ] Test data import

### Phase 4: Go-Live
- [ ] Update DNS records
- [ ] Configure SSL certificates
- [ ] Final smoke tests
- [ ] Backup both servers

## Server Credentials

### App Server (192.168.20.10)
```
User: zubair
Password: erp
Root Password: erp
SSH: Public key enabled
```

### Database Server (192.168.20.11)
```
User: zubair
Password: sql
Root Password: sql
SSH: Public key enabled
PostgreSQL User: zubair
PostgreSQL Password: zubair@0862 (from checkpoint)
Database: tradify
```

## Key Files & Configurations

### From PostgreSQL Checkpoint (Nov 16, 2025)
- Location: `BACKUPS/postgres_checkpoint_2025-11-16_09-14-23/`
- Contains: `settings_postgres.py` with PostgreSQL configuration

### Data for Import
- Primary: `prod_data_complete_backup.json`
- Location: `TradifyERP/prod_data_complete_backup.json`
- Size: Complete production database export

### Application Code
- Location: `TradifyERP/` directory
- All modules, static files, templates included

## Next Steps

1. **Verify server accessibility** - Confirm SSH access to both servers
2. **Database server setup** - Install PostgreSQL and configure
3. **Application server setup** - Install dependencies and deploy code
4. **Data import** - Load production backup
5. **Configuration** - Update settings for remote database connection
6. **Testing** - Verify all functionality
7. **Go-live** - Switch DNS and enable production traffic

## Configuration Details

### PostgreSQL Connection String
```
DATABASE_HOST=192.168.20.11
DATABASE_NAME=tradify
DATABASE_USER=zubair
DATABASE_PASSWORD=zubair@0862
DATABASE_PORT=5432
```

### Gunicorn Configuration
```
Workers: 8
Bind: 127.0.0.1:8000
Timeout: 120
```

### Nginx Configuration
```
Upstream: localhost:8000
Port: 80/443
Domain: tradifyglobal.com
```

## Important Notes

✅ UI/Theme will be identical to original (Minia + light green)
✅ All modules and functionality preserved
✅ Separate database server = better performance and security
✅ Data import from complete backup = no data loss
✅ PostgreSQL checkpoint provides working configuration

## Rollback Plan

If issues occur:
1. Restore from snapshots
2. Revert to old server IP
3. Use PostgreSQL checkpoint settings

---

**Created by:** GitHub Copilot
**Status:** Ready for deployment
**Last Updated:** December 13, 2025
