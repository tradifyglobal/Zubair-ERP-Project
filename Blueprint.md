# TradifyERP Production Server - Directory Structure Blueprint

## Complete Directory Structure

```
/var/www/tradifyerp/                          # ROOT - Project Parent Directory
├── venv/                                      # Python Virtual Environment
│   ├── bin/
│   │   ├── python3.12                        # Python Interpreter
│   │   ├── gunicorn                          # Gunicorn WSGI Server
│   │   └── activate                          # Venv activation script
│   └── lib/python3.12/site-packages/         # Installed Python packages
│
├── TradifyERP/                                # DJANGO PROJECT ROOT (manage.py location)
│   ├── manage.py                             # Django management script
│   ├── db.sqlite3                            # Development SQLite (not used in production)
│   ├── wsgi_production.py                    # WSGI Entry Point (copied here)
│   ├── local_settings.py                     # Production overrides
│   ├── requirements.txt                      # Python dependencies
│   ├── gunicorn.sock                         # Gunicorn Unix socket (for Nginx)
│   │
│   ├── TradifyERP/                           # DJANGO PACKAGE (Settings & Core Config)
│   │   ├── __init__.py
│   │   ├── settings.py                       # Django Settings (BASE_DIR points here)
│   │   ├── urls.py                           # Main URL Router
│   │   ├── asgi.py                           # ASGI Entry Point
│   │   ├── wsgi.py                           # Default WSGI Entry Point
│   │   ├── wsgi_production.py                # ⭐ PRODUCTION WSGI (PRIMARY)
│   │   ├── local_settings.py                 # Local production overrides
│   │   ├── account_adapter.py                # Authentication adapter
│   │   └── __pycache__/
│   │
│   ├── accounting/                           # Core Module - Accounting
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   ├── migrations/
│   │   ├── templates/accounting/
│   │   └── static/accounting/
│   │
│   ├── shareholder/                          # Module - Shareholder Management
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── templates/shareholder/
│   │   └── migrations/
│   │
│   ├── inventory/                            # Module - Inventory
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── templates/inventory/
│   │   └── migrations/
│   │
│   ├── sales/                                # Module - Sales
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── templates/sales/
│   │   └── migrations/
│   │
│   ├── hr/                                   # Module - Human Resources
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── templates/hr/
│   │
│   ├── ap/                                   # Module - Accounts Payable
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── templates/ap/
│   │
│   ├── ar/                                   # Module - Accounts Receivable
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── templates/ar/
│   │
│   ├── manufacturing/                        # Module - Manufacturing
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── templates/manufacturing/
│   │
│   ├── procurement/                          # Module - Procurement
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── templates/procurement/
│   │
│   ├── cash_management/                      # Module - Cash Management
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── templates/cash_management/
│   │
│   ├── crm/                                  # Module - CRM
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── templates/crm/
│   │
│   ├── expenses/                             # Module - Expenses
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── templates/expenses/
│   │
│   ├── projects/                             # Module - Projects
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── templates/projects/
│   │
│   ├── maintenance/                          # Module - Maintenance
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── templates/maintenance/
│   │
│   ├── apps/                                 # Module - Apps (Core Features)
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── migrations/
│   │
│   ├── pages/                                # Module - Pages
│   │   ├── models.py
│   │   ├── views.py
│   │   └── urls.py
│   │
│   ├── templates/                            # ⭐ PRIMARY TEMPLATES (Project Root)
│   │   ├── dashboard.html                   # Main dashboard template
│   │   ├── base.html                        # Base template (when included from partials/)
│   │   ├── partials/
│   │   │   ├── base.html                    # ⭐ Main base template
│   │   │   ├── sidebar.html                 # Vertical sidebar navigation
│   │   │   ├── hori-sidebar.html            # ⭐ Horizontal sidebar (FIXED)
│   │   │   ├── hori-header.html             # ⭐ Horizontal header (FIXED)
│   │   │   ├── header.html                  # Header component
│   │   │   ├── footer.html                  # Footer component
│   │   │   ├── rightsidebar.html            # Right sidebar
│   │   │   ├── breadcrumb.html              # Breadcrumb component
│   │   │   ├── css.html                     # CSS includes
│   │   │   └── js.html                      # JavaScript includes
│   │   ├── accounting/
│   │   │   ├── dashboard.html
│   │   │   └── ...
│   │   ├── shareholder/
│   │   └── ...
│   │
│   ├── static/                               # Static Files (CSS, JS, Images)
│   │   ├── css/
│   │   │   ├── bootstrap.min.css
│   │   │   ├── app.min.css
│   │   │   ├── icons.min.css
│   │   │   └── ...
│   │   ├── js/
│   │   │   ├── bootstrap.bundle.min.js
│   │   │   └── ...
│   │   └── images/
│   │       ├── logo.png
│   │       └── favicon.ico
│   │
│   ├── staticfiles/                          # ⭐ COLLECTED STATIC FILES (for production)
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   │
│   ├── media/                                # User Uploaded Files
│   │   ├── uploads/
│   │   └── documents/
│   │
│   ├── BACKUPS/                              # Database Backups
│   │   └── tradifyerp_db_backup_*.sql.gz
│   │
│   ├── Readme-Files/
│   ├── stakeholder_docs/
│   ├── Test-files/
│   └── utils/
│
├── Minia-Django/                             # FALLBACK ADMIN TEMPLATES (from Minia theme)
│   ├── Admin/
│   │   ├── templates/
│   │   │   ├── partials/
│   │   │   │   ├── hori-sidebar.html        # (Has problematic 'apps:' URLs - FIXED)
│   │   │   │   ├── header.html
│   │   │   │   └── ...
│   │   │   ├── apps/
│   │   │   │   ├── blogs/
│   │   │   │   ├── contacts/
│   │   │   │   ├── email/
│   │   │   │   └── ...
│   │   │   └── elements/
│   │   │       ├── components/
│   │   │       └── extended/
│   │   ├── static/
│   │   │   ├── css/
│   │   │   ├── js/
│   │   │   ├── images/
│   │   │   └── libs/
│   │   ├── elements/
│   │   │   ├── urls.py
│   │   │   └── views.py
│   │   └── ...
│   └── Starterkit/
│
└── nginx_tradifyglobal.conf                  # Nginx configuration (for reference)
```

---

## Key Directory Roles

| Path | Purpose | Notes |
|------|---------|-------|
| `/var/www/tradifyerp/` | Parent project root | Contains venv, manage.py location |
| `/var/www/tradifyerp/venv/` | Python virtual environment | Isolated Python packages |
| `/var/www/tradifyerp/TradifyERP/` | Django project root | Where gunicorn runs from |
| `/var/www/tradifyerp/TradifyERP/TradifyERP/` | Django package | Contains settings.py, urls.py, wsgi_production.py |
| `/var/www/tradifyerp/TradifyERP/templates/` | ⭐ Primary templates | Loaded first (highest priority) |
| `/var/www/Minia-Django/Admin/templates/` | Fallback templates | Fallback only (lower priority) |
| `/var/www/tradifyerp/TradifyERP/staticfiles/` | Collected static files | For Nginx serving |
| `/var/www/tradifyerp/TradifyERP/media/` | User uploads | Dynamically generated |

---

## Critical Configuration Files

```
/var/www/tradifyerp/TradifyERP/TradifyERP/
├── settings.py              # BASE_DIR = /var/www/tradifyerp/TradifyERP
├── wsgi_production.py       # ⭐ Working directory: /var/www/tradifyerp/TradifyERP
└── local_settings.py        # PostgreSQL config, DEBUG=True
```

### settings.py Configuration
```python
BASE_DIR = Path(__file__).resolve().parent.parent
# Resolves to: /var/www/tradifyerp/TradifyERP

TEMPLATES = [
    {
        'DIRS': [
            str(BASE_DIR / 'templates'),  # /var/www/tradifyerp/TradifyERP/templates
            str(ADMIN_PATH / 'templates'),  # /var/www/Minia-Django/Admin/templates (fallback)
        ],
    }
]

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # /var/www/tradifyerp/TradifyERP/staticfiles

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'  # /var/www/tradifyerp/TradifyERP/media
```

### wsgi_production.py Configuration
```python
# STEP 1: Working directory
os.chdir('/var/www/tradifyerp/TradifyERP')

# STEP 2: sys.path includes both project root and parent
PROJECT_ROOT = '/var/www/tradifyerp/TradifyERP'
PARENT_ROOT = '/var/www/tradifyerp'
sys.path = [PROJECT_ROOT, PARENT_ROOT] + [p for p in sys.path if ...]

# STEP 3: Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'TradifyERP.settings'
```

---

## Service Configurations

### Gunicorn
```
Started from:     /var/www/tradifyerp/TradifyERP/
Command:          gunicorn TradifyERP.wsgi_production:application
Socket:           /var/www/tradifyerp/gunicorn.sock
Workers:          8 (+ 1 master process)
Worker Class:     sync
Binding:          Unix socket (for Nginx)
Access Log:       /var/log/tradifyerp/gunicorn_access.log
Error Log:        /var/log/tradifyerp/gunicorn_error.log
```

### Nginx
```
Configuration:    /etc/nginx/sites-available/tradifyglobal.com
Server:           192.168.2.185 (port 80/443)
Proxy Pass:       unix:/var/www/tradifyerp/gunicorn.sock
SSL:              Let's Encrypt / HTTPS
Static Files:     /var/www/tradifyerp/TradifyERP/staticfiles/
Media Files:      /var/www/tradifyerp/TradifyERP/media/
```

### PostgreSQL
```
Database:         tradifyerp_db
User:             tradifyerp_user
Password:         Tradify@PostgreSQL2024
Host:             localhost
Port:             5432
Configuration:    /etc/postgresql/16/main/postgresql.conf
```

---

## Python Path Resolution

### How Python Finds Modules

When gunicorn starts with:
```bash
cd /var/www/tradifyerp/TradifyERP
gunicorn TradifyERP.wsgi_production:application
```

sys.path includes:
1. `/var/www/tradifyerp/TradifyERP` - finds all apps (inventory, accounting, etc.)
2. `/var/www/tradifyerp` - finds the TradifyERP package

Module resolution:
- `import inventory` → `/var/www/tradifyerp/TradifyERP/inventory/`
- `import TradifyERP` → `/var/www/tradifyerp/TradifyERP/`
- `from TradifyERP.settings import ...` → `/var/www/tradifyerp/TradifyERP/TradifyERP/settings.py`
- `from TradifyERP.wsgi_production import ...` → `/var/www/tradifyerp/TradifyERP/TradifyERP/wsgi_production.py`

---

## Template Loading Priority

Templates are loaded in this order (first match wins):

1. **`/var/www/tradifyerp/TradifyERP/templates/`** (PRIMARY - Highest Priority)
   - Project templates
   - Module-specific templates
   - Custom overrides

2. **`/var/www/Minia-Django/Admin/templates/`** (FALLBACK - Lower Priority)
   - Default admin templates from Minia theme
   - Only used if not found in primary

### Example: dashboard.html
- Check: `/var/www/tradifyerp/TradifyERP/templates/dashboard.html` ✓ Found → Use this
- If not found, check: `/var/www/Minia-Django/Admin/templates/dashboard.html`

### Example: accounting/dashboard.html
- Check: `/var/www/tradifyerp/TradifyERP/templates/accounting/dashboard.html` ✓ Found → Use this
- If not found, check: `/var/www/Minia-Django/Admin/templates/accounting/dashboard.html`

---

## Static Files & Collectstatic

### Development
```
/var/www/tradifyerp/TradifyERP/static/
  ├── css/
  ├── js/
  └── images/
```

### Production
```
/var/www/tradifyerp/TradifyERP/staticfiles/  (collected & minified)
  ├── css/
  ├── js/
  └── images/
```

**Collection Command:**
```bash
python manage.py collectstatic --noinput
```

**Nginx Serves From:**
```
location /static/ {
    alias /var/www/tradifyerp/TradifyERP/staticfiles/;
}
```

---

## Database Backups

Location: `/var/www/tradifyerp/TradifyERP/BACKUPS/`

Naming Convention: `tradifyerp_db_backup_YYYYMMDD_HHMMSS.sql.gz`

Example:
```
tradifyerp_db_backup_2025-12-11_07-30-45.sql.gz
```

**Backup Command:**
```bash
su - postgres -c 'pg_dump -d tradifyerp_db' | gzip > /var/www/tradifyerp/BACKUPS/tradifyerp_db_backup_$(date +%Y%m%d_%H%M%S).sql.gz
```

**Restore Command:**
```bash
gunzip -c /var/www/tradifyerp/BACKUPS/tradifyerp_db_backup_YYYYMMDD_HHMMSS.sql.gz | psql -d tradifyerp_db -U tradifyerp_user
```

---

## PostgreSQL Database Details & Credentials

### Connection Information

| Setting | Value | Notes |
|---------|-------|-------|
| **Database Name** | `tradifyerp_db` | Primary production database |
| **Database User** | `tradifyerp_user` | Database owner & connection user |
| **User Password** | `Tradify@PostgreSQL2024` | ⚠️ Keep secure - change in production! |
| **Host** | `localhost` | Local socket connection only |
| **Port** | `5432` | PostgreSQL default port |
| **Connection Type** | Unix socket (local) | Remote connections disabled |
| **Encoding** | `UTF-8` | Unicode support enabled |
| **Locale** | `en_US.UTF-8` | Language & collation |

### PostgreSQL Version & Configuration

```
PostgreSQL Version:  16.11 (Ubuntu 16.11-0ubuntu0.24.04.1)
Compiled:            gcc (Ubuntu 13.3.0-6ubuntu2~24.04) 13.3.0, 64-bit
Architecture:        x86_64-pc-linux-gnu
Service Status:      Active and running
Config Location:     /etc/postgresql/16/main/postgresql.conf
HBA File:            /etc/postgresql/16/main/pg_hba.conf
```

### Django Database Configuration

Located in: `/var/www/tradifyerp/TradifyERP/TradifyERP/local_settings.py`

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'tradifyerp_db',
        'USER': 'tradifyerp_user',
        'PASSWORD': 'Tradify@PostgreSQL2024',
        'HOST': 'localhost',
        'PORT': '5432',
        'ATOMIC_REQUESTS': True,
        'CONN_MAX_AGE': 600,
    }
}
```

### Connection String

**psql Command Line:**
```bash
psql -U tradifyerp_user -d tradifyerp_db -h localhost
```

**Python Connection:**
```python
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    database='tradifyerp_db',
    user='tradifyerp_user',
    password='Tradify@PostgreSQL2024',
    port=5432
)
```

**Django Connection:**
```python
from django.db import connections

db_conn = connections['default']
cursor = db_conn.cursor()
```

### Database Schema & Tables

**Core Tables (Examples):**
```
accounting_entity               # Companies/entities
accounting_ledger_entry         # GL entries
accounting_account              # Chart of accounts
accounting_account_balance      # Account balances
accounting_customer             # Customer records
accounting_vendor               # Vendor records
accounting_invoice              # Invoices
accounting_payment              # Payments

shareholder_shareholder         # Shareholder records
shareholder_capital_contribution # Capital contributions
shareholder_investment_history  # Investment transactions

inventory_item                  # Inventory items
inventory_warehouse             # Storage locations
inventory_movement              # Inventory transactions

sales_order                      # Sales orders
sales_invoice                    # Sales invoices
sales_line_item                 # Order/invoice line items

hr_employee                      # Employee records
hr_payroll                       # Payroll records
hr_attendance                    # Attendance records

auth_user                        # Django user accounts
auth_group                       # User groups
auth_permission                  # Permission definitions
```

### Database Maintenance Commands

**Check Database Size:**
```bash
psql -U tradifyerp_user -d tradifyerp_db -c "SELECT pg_size_pretty(pg_database_size('tradifyerp_db'));"
```

**Connect to Database:**
```bash
psql -U tradifyerp_user -d tradifyerp_db
```

**List All Tables:**
```bash
psql -U tradifyerp_user -d tradifyerp_db -c "\dt"
```

**Backup Database:**
```bash
pg_dump -U tradifyerp_user -d tradifyerp_db > tradifyerp_db_backup.sql

# Compressed backup
pg_dump -U tradifyerp_user -d tradifyerp_db | gzip > tradifyerp_db_backup.sql.gz
```

**Restore Database:**
```bash
psql -U tradifyerp_user -d tradifyerp_db < tradifyerp_db_backup.sql

# From compressed backup
gunzip -c tradifyerp_db_backup.sql.gz | psql -U tradifyerp_user -d tradifyerp_db
```

**Run Vacuum & Analyze (Maintenance):**
```bash
psql -U tradifyerp_user -d tradifyerp_db -c "VACUUM ANALYZE;"
```

**Check Connection Count:**
```bash
psql -U tradifyerp_user -d tradifyerp_db -c "SELECT count(*) FROM pg_stat_activity WHERE datname='tradifyerp_db';"
```

### Performance Monitoring

**Current Active Connections:**
```bash
psql -U tradifyerp_user -d tradifyerp_db -c "SELECT usename, application_name, state FROM pg_stat_activity WHERE datname='tradifyerp_db';"
```

**Table Sizes:**
```bash
psql -U tradifyerp_user -d tradifyerp_db -c "SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) FROM pg_tables ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC LIMIT 20;"
```

**Query Statistics (Slow Queries):**
```bash
psql -U tradifyerp_user -d tradifyerp_db -c "SELECT query, calls, total_time, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"
```

### User Management

**Create Additional User:**
```bash
sudo -u postgres createuser -P new_username
# Then grant permissions:
psql -U postgres -d tradifyerp_db -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO new_username;"
```

**Reset User Password:**
```bash
sudo -u postgres psql -c "ALTER USER tradifyerp_user WITH PASSWORD 'NewPassword123';"
```

**List All Users:**
```bash
psql -U postgres -c "\du"
```

### Backup Strategy

**Automated Daily Backup (via cron):**
```bash
# Add to crontab: crontab -e
0 2 * * * pg_dump -U tradifyerp_user -d tradifyerp_db | gzip > /var/www/tradifyerp/BACKUPS/tradifyerp_db_backup_$(date +\%Y\%m\%d_\%H\%M\%S).sql.gz
```

**Backup Retention (Keep last 30 days):**
```bash
find /var/www/tradifyerp/BACKUPS -name "*.sql.gz" -mtime +30 -delete
```

### Database Security Checklist

- ✅ Remote connections disabled (localhost only)
- ✅ Strong password configured: `Tradify@PostgreSQL2024`
- ✅ Dedicated database user: `tradifyerp_user`
- ✅ Atomic requests enabled in Django
- ✅ Connection pooling (CONN_MAX_AGE: 600 seconds)
- ⚠️ TODO: Change password in production to unique/stronger value
- ⚠️ TODO: Enable SSL for PostgreSQL
- ⚠️ TODO: Configure WAL (Write-Ahead Logging) for backup

### Connection Pool Settings (Django)

```python
CONN_MAX_AGE = 600          # Reuse connections for 10 minutes
ATOMIC_REQUESTS = True      # Each request is a transaction
```

### Common PostgreSQL Issues & Solutions

**Issue: "Too many connections"**
```bash
# Check current connections
psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"

# Increase max_connections in postgresql.conf:
max_connections = 200

# Restart PostgreSQL
sudo systemctl restart postgresql
```

**Issue: Database locked**
```bash
# Terminate idle connections
psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='tradifyerp_db' AND state='idle';"
```

**Issue: Disk space issues**
```bash
# Check database size
psql -U tradifyerp_user -d tradifyerp_db -c "SELECT pg_size_pretty(pg_database_size('tradifyerp_db'));"

# Run vacuum to reclaim space
psql -U tradifyerp_user -d tradifyerp_db -c "VACUUM FULL ANALYZE;"
```

---

## Important Notes

### Path Requirements
- ✅ Gunicorn MUST run from `/var/www/tradifyerp/TradifyERP/`
- ✅ sys.path must include both `/var/www/tradifyerp/TradifyERP` and `/var/www/tradifyerp`
- ✅ WSGI module must be `TradifyERP.wsgi_production:application`
- ✅ BASE_DIR must point to `/var/www/tradifyerp/TradifyERP/`

### Fixed Issues
- ✅ Removed all `{% url 'apps:...' %}` template references
- ✅ Removed all `{% url 'elements:...' %}` template references
- ✅ Fixed BASE_DIR calculation in settings.py
- ✅ Fixed Python path in wsgi_production.py
- ✅ Deployed wsgi_production.py to correct location

### Template Safety
- All template files use proper Django template tags
- No problematic URL namespace references
- Primary templates override Minia fallbacks
- All includes properly resolved

---

## Login Credentials (Test)

```
Username: zubair
Password: Zub@ir0861
```

---

## Current Server Status

```
✅ Gunicorn:    18 processes (1 master + 8 workers)
✅ PostgreSQL:  Active and responding
✅ Nginx:       Running and proxying
✅ Login Page:  HTTP 200 (loads successfully)
✅ Dashboard:   HTTP 302 (redirects as expected)
✅ No Errors:   All paths resolved correctly
```

---

**Last Updated:** December 11, 2025
**Status:** Production Ready ✅
