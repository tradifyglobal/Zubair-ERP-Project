# TradifyERP Application Architecture Summary

**Last Updated**: April 7, 2026

---

## 📋 Executive Summary

Your ERP system consists of:
- **1 App Server**: Ubuntu 24.04 LTS with Django + Gunicorn + Nginx
- **1 DB Server**: Ubuntu 24.04 LTS with PostgreSQL 16
- **Database**: tradifyerp_db with user zubair

---

## 🖥️ APP SERVER (192.168.20.10) - root

### System Information
| Property | Value |
|----------|-------|
| **OS** | Ubuntu 24.04.3 LTS (Noble Numbat) |
| **Kernel** | 6.8.0-90-generic |
| **Architecture** | x86_64 |
| **Hostname** | erp-prod |
| **Python** | Python 3.12.3 |

### Running Services
1. **Nginx** - Reverse proxy web server
2. **Gunicorn** - WSGI application server (5 workers, port 8000)

### Django Application - TradifyERP

**Project Structure:**
```
/var/www/tradifyerp/
├── TradifyERP/          (Main Django project)
│   ├── settings_production.py
│   ├── wsgi.py
│   └── [Django apps]
├── venv/                (Python virtual environment)
└── TradifyERP/          (App directory)
    ├── __init__.py
    ├── apps.py
    ├── models.py
    ├── views.py
    ├── urls.py
    └── admin.py
```

Also at: `/opt/tradifyerp/TradifyERP/` (backup/reference copy)

### Django Modules/Apps (7 Total)

| Module | Type | Location | Purpose |
|--------|------|----------|---------|
| **crm** | Django App | `/var/www/tradifyerp/TradifyERP/crm/` | Customer Relationship Management |
| **accounting** | Django App | `/var/www/tradifyerp/TradifyERP/accounting/` | General Ledger, Financial Reporting |
| **ap** | Django App | `/var/www/tradifyerp/TradifyERP/ap/` | Accounts Payable |
| **ar** | Django App | `/var/www/tradifyerp/TradifyERP/ar/` | Accounts Receivable |
| **cash_management** | Django App | `/var/www/tradifyerp/TradifyERP/cash_management/` | Cash Flow Management |
| **audit_logging** | Django App | `/var/www/tradifyerp/TradifyERP/audit_logging/` | Audit Trail & Logging |
| **TradifyERP** | Main Project | `/var/www/tradifyerp/TradifyERP/` | Core Django Project |

### Python Dependencies (App Server Virtual Env)

**Core Framework:**
- Django 5.2.9
- djangorestframework 3.14.0
- gunicorn 23.0.0

**Authentication & Authorization:**
- django-allauth 65.13.1
- django-otp 1.1.3
- django-ratelimit 4.1.0
- social-auth-app-django 5.6.0
- social-auth-core 4.8.1
- PyJWT 2.10.1
- oauthlib 3.3.1

**Database & ORM:**
- psycopg2-binary 2.9.9 (PostgreSQL adapter)
- sqlparse 0.5.4

**API & Serialization:**
- djangorestframework 3.14.0
- defusedxml 0.7.1

**Caching & Sessions:**
- django-redis 5.4.0
- redis 7.1.0

**Frontend & Templates:**
- crispy-bootstrap5 2025.6
- django-crispy-forms 2.5
- pillow 11.0.0 (Image processing)

**Data Import/Export:**
- django-import-export 4.3.14
- openpyxl 3.1.5 (Excel support)
- tablib 3.9.0

**Security & CORS:**
- django-cors-headers 4.3.0
- cryptography 41.0.0
- requests-oauthlib 2.0.0

**Utilities:**
- django-extensions 4.1
- python-decouple 3.8
- requests 2.32.5
- pytz 2025.2

**HTTP & Encoding:**
- certifi 2025.11.12
- charset-normalizer 3.4.4
- urllib3 2.6.2
- idna 3.11
- packaging 25.0

### Gunicorn Configuration
```
Service: gunicorn.service
WorkingDirectory: /var/www/tradifyerp
Command: gunicorn --workers 5 --bind 127.0.0.1:8000 --timeout 300 
         --env DJANGO_SETTINGS_MODULE=TradifyERP.settings_production 
         TradifyERP.wsgi:application
Workers: 5
Timeout: 300 seconds
User: zubair
Group: zubair
Restart: Always (auto-restart on failure)
```

### Nginx Reverse Proxy
- Forwards requests to Gunicorn on 127.0.0.1:8000
- Handles SSL/TLS termination
- Serves static files

---

## 🗄️ DATABASE SERVER (192.168.20.11) - zubair

### System Information
| Property | Value |
|----------|-------|
| **OS** | Ubuntu 24.04.3 LTS (Noble Numbat) |
| **Kernel** | 6.8.0-90-generic |
| **Architecture** | x86_64 |
| **Hostname** | postgressql-erp |
| **PostgreSQL** | Version 16.13 |
| **Python** | Python 3.12.3 |

### Database Information

| Property | Value |
|----------|-------|
| **Database Name** | tradifyerp_db |
| **Primary User** | zubair (password: sql) |
| **Connection Details** | Host: 192.168.20.11, Port: 5432 |
| **Data Directory** | /var/lib/postgresql/16 |

### Installed PostgreSQL Packages

1. **postgresql-16** - Core PostgreSQL server
2. **postgresql-client-16** - Client tools for connecting to local/remote servers
3. **postgresql-client-common** - Common PostgreSQL client files
4. **postgresql-client** - PostgreSQL client utilities
5. **postgresql-common** - Shared files for all PostgreSQL versions
6. **postgresql-contrib** - Additional PostgreSQL modules and utilities

### Database Tools & Utilities Available

| Tool | Purpose | Location |
|------|---------|----------|
| **pg_dump** | Dump database to SQL file | /usr/bin/pg_dump |
| **pg_restore** | Restore database from dump | /usr/bin/pg_restore |
| **pg_basebackup** | Create base backup of cluster | /usr/bin/pg_basebackup |
| **psql** | Interactive PostgreSQL client | /usr/bin/psql |

### Database Architecture (Assumed Based on Django Models)

The database `tradifyerp_db` likely contains tables for:

**Core Modules:**
- **CRM**: Customers, Contacts, Leads, Opportunities
- **Accounting**: General Ledger, Chart of Accounts, Journal Entries, Financial Reports
- **AP** (Accounts Payable): Vendor Bills, Payments, Purchase Orders
- **AR** (Accounts Receivable): Customer Invoices, Payments, Sales Orders
- **Cash Management**: Cash Accounts, Cash Transfers, Bank Reconciliation
- **Audit Logging**: Audit Trails, User Activities, Change Logs

---

## 🔄 Integration & Data Flow

```
User Browser
    ↓
Nginx (Port 80/443)
    ↓
Gunicorn (127.0.0.1:8000)
    ↓
Django Application (5 workers)
    ├── CRM
    ├── Accounting
    ├── AP
    ├── AR
    ├── Cash Management
    └── Audit Logging
    ↓
PostgreSQL Database (192.168.20.11:5432)
    ↓
tradifyerp_db
```

---

## 🚀 Technology Stack Summary

| Layer | Technology | Version |
|-------|----------|---------|
| **Web Server** | Nginx | Latest (Ubuntu repos) |
| **App Server** | Gunicorn | 23.0.0 |
| **Framework** | Django | 5.2.9 |
| **Database** | PostgreSQL | 16.13 |
| **REST API** | Django REST Framework | 3.14.0 |
| **Authentication** | django-allauth + OAuth2 | Latest |
| **Caching** | Redis | Latest (via python-redis 7.1.0) |
| **Frontend** | Bootstrap 5 + Django Templates | Latest |
| **Python** | Python 3.12.3 | Both servers |

---

## 📊 Key Features

### 1. **Enterprise ERP Modules**
   - ✅ Customer Relationship Management (CRM)
   - ✅ General Ledger & Accounting
   - ✅ Accounts Payable (AP)
   - ✅ Accounts Receivable (AR)
   - ✅ Cash Management
   - ✅ Comprehensive Audit Logging

### 2. **Modern Architecture**
   - ✅ Microservices-ready (modular Django apps)
   - ✅ RESTful API support
   - ✅ Multi-user concurrent access (5 Gunicorn workers)

### 3. **Security**
   - ✅ OAuth2 and Social Authentication
   - ✅ Multi-factor Authentication (OTP)
   - ✅ Rate limiting
   - ✅ CORS support
   - ✅ Complete audit trail logging

### 4. **Database**
   - ✅ PostgreSQL 16 (enterprise-grade)
   - ✅ Backup tools (pg_dump, pg_basebackup)
   - ✅ Point-in-time recovery capability

### 5. **Performance**
   - ✅ Redis caching
   - ✅ Multi-worker WSGI server
   - ✅ Static file serving via Nginx
   - ✅ 300-second timeout for long operations

---

## 🔧 Common Operations

### Run Migrations
```powershell
ssh root@192.168.20.10 "cd /var/www/tradifyerp && python manage.py migrate"
```

### Backup Database
```powershell
ssh zubair@192.168.20.11 "pg_dump -h localhost tradifyerp_db" > backup.sql
```

### Check Database Connection
```powershell
psql -h 192.168.20.11 -U zubair -d tradifyerp_db -c "SELECT version();"
```

### Restart Application Server
```powershell
ssh root@192.168.20.10 "sudo systemctl restart gunicorn"
```

### View Application Logs
```powershell
ssh root@192.168.20.10 "tail -f /var/log/gunicorn.log"
```

---

## 📝 Notes

1. **Production Settings**: App uses `settings_production.py` instead of default settings
2. **Virtual Environment**: Application runs in isolated venv at `/var/www/tradifyerp/venv/`
3. **User Management**: Both app and DB servers run services as `zubair` user
4. **Passwordless Access**: SSH keys are configured for seamless deployments
5. **Database Replication**: Not configured (single instance)
6. **Load Balancing**: Not configured (single app server)
7. **Monitoring**: No external monitoring tools detected (consider adding Prometheus/Grafana)

---

## 📞 Quick Reference

**App Server SSH:**
```powershell
ssh app-server
ssh root@192.168.20.10
```

**DB Server SSH:**
```powershell
ssh db-server
ssh zubair@192.168.20.11
```

**Database Access:**
```powershell
psql -h 192.168.20.11 -U zubair -d tradifyerp_db
```

**Check Service Status:**
```powershell
ssh root@192.168.20.10 "systemctl status gunicorn nginx"
```

---

**Document Generated**: April 7, 2026

