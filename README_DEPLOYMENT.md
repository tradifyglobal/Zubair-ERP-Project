# TradifyERP New Server Deployment Package

**Created:** December 13, 2025
**Status:** Ready for Deployment
**Architecture:** Two-Server (Application + Database)

---

## Quick Start

### For Automated Deployment (Recommended)
```bash
cd f:\ERP-Production\Zubair-ERP-Project
bash DEPLOY_NEW_SERVERS.sh
```

### For Manual Deployment
See `MANUAL_DEPLOYMENT_GUIDE.md` for step-by-step instructions.

---

## Servers

| Server | IP | Role | User | Password |
|--------|-----|------|------|----------|
| Server 1 | 192.168.2.69 | Django App + Nginx | zubair | erp |
| Server 2 | 192.168.2.59 | PostgreSQL Database | zubair | sql |

---

## Files Included

### Setup Scripts
- **setup_postgresql_server.sh** - Installs and configures PostgreSQL
- **setup_django_server.sh** - Installs Django and dependencies
- **DEPLOY_NEW_SERVERS.sh** - Automated deployment orchestration

### Configuration Files
- **nginx_tradifyglobal_prod.conf** - Nginx web server config
- **settings_production.py** - Django PostgreSQL settings
- **gunicorn_config.py** - Gunicorn application server config

### Documentation
- **DEPLOYMENT_GUIDE_NEW_SERVERS.md** - High-level overview
- **MANUAL_DEPLOYMENT_GUIDE.md** - Step-by-step instructions
- **DEPLOYMENT_SUMMARY.md** - Complete reference guide
- **DEPLOYMENT_VERIFICATION_CHECKLIST.md** - Testing checklist
- **README_DEPLOYMENT.md** - This file

### Data & Backups
- **prod_data_complete_backup.json** - Production data (Django fixture)
- **BACKUPS/postgres_checkpoint_2025-11-16_09-14-23/** - PostgreSQL config

---

## Architecture

```
┌─────────────────────────────────────┐
│   Application Server 192.168.2.69   │
│   - Django 5.2.9                    │
│   - Gunicorn 23.0.0                 │
│   - Nginx 1.24.0                    │
│   - Python 3.12.3                   │
│   - User: zubair                    │
└────────────────┬────────────────────┘
                 │
        PostgreSQL Connection (Port 5432)
                 │
┌────────────────▼────────────────────┐
│   Database Server 192.168.2.59      │
│   - PostgreSQL 16.11                │
│   - Database: tradify               │
│   - User: zubair                    │
│   - Password: zubair@0862           │
└─────────────────────────────────────┘
```

---

## Deployment Steps

### Step 1: Pre-Deployment
- Verify both servers are online
- Verify SSH access to both servers
- Confirm network connectivity between servers

### Step 2: Database Setup (192.168.2.59)
- Install PostgreSQL 16
- Create database 'tradify' and user 'zubair'
- Configure for remote connections
- Test connection from app server

### Step 3: Application Setup (192.168.2.69)
- Install Python 3.12 and dependencies
- Create virtual environment
- Install Python packages
- Deploy Django code

### Step 4: Configuration
- Configure Django settings for remote PostgreSQL
- Configure Nginx as reverse proxy
- Configure Gunicorn application server

### Step 5: Database Initialization
- Run Django migrations
- Collect static files
- Create log directories

### Step 6: Data Import
- Copy production backup to app server
- Import data using Django loaddata command
- Verify data integrity

### Step 7: Start Services
- Start Gunicorn
- Start Nginx
- Verify services are running

### Step 8: Verification
- Test web application
- Test all modules
- Verify UI theme (Minia + light green)
- Verify Tradify logo
- Test data access

---

## Database Details

**PostgreSQL Configuration:**
- **Host:** 192.168.2.59
- **Port:** 5432
- **Database:** tradify
- **User:** zubair
- **Password:** zubair@0862
- **Connection from:** 192.168.2.69 (app server)

---

## Access After Deployment

**Web Application:**
- URL: http://192.168.2.69/
- Dashboard: http://192.168.2.69/accounting/dashboard/
- Admin: http://192.168.2.69/admin/

**SSH Access:**
```bash
# App server
ssh zubair@192.168.2.69

# Database server
ssh zubair@192.168.2.59

# Database connection
psql -h 192.168.2.59 -U zubair -d tradify
```

---

## Features & Modules

✅ **Accounting Module**
- Chart of Accounts
- Ledger Entries
- Trial Balance
- Financial Reports

✅ **Sales Module**
- Orders & Invoices
- Quotations
- Pricing & Discounts
- Accounts Receivable

✅ **CRM Module**
- Leads Management
- Opportunities
- Campaigns
- Contacts

✅ **HR Module**
- Employee Management
- Payroll
- Leave Management
- Performance Reviews

✅ **Inventory Module**
- Products & Categories
- Stock Management
- Warehouse Tracking
- Purchase Orders

✅ **Additional Modules**
- Shareholder Management
- Procurement
- Manufacturing
- Projects
- Expenses
- Cash Management

---

## UI/Theme

**Preserved from Original:**
✅ Minia Theme Framework
✅ Light Green Color Scheme
✅ Tradify Logo & Branding
✅ Responsive Design
✅ All Customizations

---

## Estimated Timeline

| Phase | Duration |
|-------|----------|
| Database Setup | 5-10 min |
| App Server Setup | 10-15 min |
| Code Deployment | 5 min |
| Migrations | 5 min |
| Data Import | 5-20 min |
| Testing | 10-15 min |
| **Total** | **40-70 min** |

---

## Security Features

✅ PostgreSQL on separate server
✅ SSH key authentication
✅ Firewall rules
✅ Django security settings
✅ HTTPS ready (after SSL setup)
✅ Secure session cookies
✅ CSRF protection
✅ XSS protection headers

---

## Backup & Recovery

**Database Backups:**
```bash
# Backup script (run regularly)
pg_dump -h 192.168.2.59 -U zubair tradify | gzip > tradify_backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Restore from backup
gunzip < tradify_backup_20251213_000000.sql.gz | psql -h 192.168.2.59 -U zubair tradify
```

**Application Code:**
- Store in Git repository
- Regular snapshots of /var/www/tradifyerp
- Backup staticfiles and media

---

## Troubleshooting

### Database Connection Issues
```bash
# Test connection from app server
psql -h 192.168.2.59 -U zubair -d tradify

# Verify PostgreSQL is listening
sudo netstat -tlnp | grep 5432

# Check firewall
sudo ufw status
```

### Gunicorn Issues
```bash
# Check status
sudo systemctl status gunicorn_tradifyerp

# View logs
sudo journalctl -u gunicorn_tradifyerp -f

# Restart
sudo systemctl restart gunicorn_tradifyerp
```

### Nginx Issues
```bash
# Test configuration
sudo nginx -t

# View error log
sudo tail -f /var/log/nginx/tradifyerp_error.log

# Restart
sudo systemctl restart nginx
```

See `MANUAL_DEPLOYMENT_GUIDE.md` for detailed troubleshooting.

---

## Support & Documentation

| Document | Purpose |
|----------|---------|
| DEPLOYMENT_GUIDE_NEW_SERVERS.md | High-level overview |
| MANUAL_DEPLOYMENT_GUIDE.md | Step-by-step instructions |
| DEPLOYMENT_SUMMARY.md | Complete reference |
| DEPLOYMENT_VERIFICATION_CHECKLIST.md | QA checklist |
| README_DEPLOYMENT.md | This file |

---

## Next Steps

1. **Review Documentation**
   - Read DEPLOYMENT_GUIDE_NEW_SERVERS.md
   - Review MANUAL_DEPLOYMENT_GUIDE.md
   - Check setup scripts

2. **Verify Servers**
   - Confirm SSH access
   - Test network connectivity
   - Verify credentials

3. **Execute Deployment**
   - Run DEPLOY_NEW_SERVERS.sh (automated)
   - Or follow MANUAL_DEPLOYMENT_GUIDE.md (manual)

4. **Verify & Test**
   - Use DEPLOYMENT_VERIFICATION_CHECKLIST.md
   - Test all modules
   - Verify theme and branding

5. **Go Live**
   - Update DNS (if needed)
   - Configure SSL (recommended)
   - Monitor services
   - Document procedures

---

## Contact & Support

For issues or questions:
1. Check MANUAL_DEPLOYMENT_GUIDE.md troubleshooting section
2. Review deployment logs
3. Check system logs:
   - Django: /var/log/tradifyerp/
   - Nginx: /var/log/nginx/
   - PostgreSQL: /var/log/postgresql/

---

## Deployment Checklist

Before starting deployment, verify:
- [ ] Both servers are online
- [ ] SSH access confirmed
- [ ] Network connectivity verified
- [ ] All files present locally
- [ ] PostgreSQL checkpoint available
- [ ] Data backup file present
- [ ] Admin credentials ready
- [ ] DNS ready (if needed)

---

**Deployment Package Created:** December 13, 2025
**Status:** ✅ Ready for Deployment
**Prepared By:** GitHub Copilot
**For:** TradifyERP Production Environment
