# TradifyERP Deployment Verification Checklist

**Date:** December 13, 2025
**Deployment Type:** Two-Server Setup (App + Database)
**App Server:** 192.168.20.10
**DB Server:** 192.168.20.11

---

## Pre-Deployment Verification

### Server Connectivity
- [ ] App server (192.168.20.10) is online and accessible
- [ ] Database server (192.168.20.11) is online and accessible
- [ ] SSH access confirmed to app server (user: zubair)
- [ ] SSH access confirmed to DB server (user: zubair)

### Local Project Files
- [ ] TradifyERP source code complete
- [ ] prod_data_complete_backup.json present
- [ ] PostgreSQL checkpoint folder available
- [ ] All setup scripts in root directory

---

## Phase Completion Tracking

### Phase 1: Database Server Setup
- [ ] PostgreSQL 16 installed
- [ ] Database 'tradify' created
- [ ] User 'zubair' created with password 'zubair@0862'
- [ ] Remote access configured
- [ ] Connection test passed

**Status:** ☐ Complete ☐ In Progress ☐ Failed

### Phase 2: Application Server Setup
- [ ] Python 3.12 installed
- [ ] Virtual environment created
- [ ] Python dependencies installed
- [ ] Django code deployed
- [ ] Settings configured for PostgreSQL

**Status:** ☐ Complete ☐ In Progress ☐ Failed

### Phase 3: Database & Migrations
- [ ] Database connection test passed
- [ ] Django migrations executed
- [ ] Database schema created
- [ ] No migration errors

**Status:** ☐ Complete ☐ In Progress ☐ Failed

### Phase 4: Static Files & Configuration
- [ ] Static files collected
- [ ] Nginx configured
- [ ] Directory permissions set
- [ ] Gunicorn configuration created

**Status:** ☐ Complete ☐ In Progress ☐ Failed

### Phase 5: Services Started
- [ ] Gunicorn service running
- [ ] Nginx service running
- [ ] Services enabled on boot
- [ ] No service errors

**Status:** ☐ Complete ☐ In Progress ☐ Failed

### Phase 6: Application Testing
- [ ] Application accessible via HTTP
- [ ] Dashboard loads
- [ ] All modules accessible
- [ ] Admin interface working

**Status:** ☐ Complete ☐ In Progress ☐ Failed

### Phase 7: Data Import
- [ ] Data file copied to server
- [ ] Data loaded into database
- [ ] No import errors
- [ ] Data verification passed

**Status:** ☐ Complete ☐ In Progress ☐ Failed

### Phase 8: UI/Theme Verification
- [ ] Minia theme active
- [ ] Light green color scheme
- [ ] Tradify logo displayed
- [ ] Responsive design working

**Status:** ☐ Complete ☐ In Progress ☐ Failed

### Phase 9: Performance & Monitoring
- [ ] Page load times acceptable
- [ ] No errors in logs
- [ ] Resource usage normal
- [ ] System stable

**Status:** ☐ Complete ☐ In Progress ☐ Failed

### Phase 10: Security & Backups
- [ ] Production security settings applied
- [ ] Backups configured
- [ ] Monitoring active
- [ ] Documentation complete

**Status:** ☐ Complete ☐ In Progress ☐ Failed

---

## Critical Issues Found

| # | Issue | Severity | Resolution | Status |
|---|-------|----------|-----------|--------|
| 1 | | HIGH/MEDIUM/LOW | | |
| 2 | | HIGH/MEDIUM/LOW | | |
| 3 | | HIGH/MEDIUM/LOW | | |

---

## Deployment Sign-Off

**Overall Status:** ☐ SUCCESS ☐ PARTIAL ☐ FAILED

**Deployed By:** _________________ **Date:** _________________

**Verified By:** _________________ **Date:** _________________

**Approved By:** _________________ **Date:** _________________

---

## Rollback Procedure (If Needed)

If deployment fails or needs rollback:
1. Stop services: `sudo systemctl stop gunicorn_tradifyerp nginx`
2. Restore from snapshot or previous backup
3. Verify database integrity
4. Update DNS (if changed)
5. Test application

**Rollback Completed:** ☐ Yes ☐ No ☐ N/A
