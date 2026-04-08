# TradifyERP Application & Modules Inventory

## 📱 DJANGO MODULES (7 Total)

### 1. **CRM** (Customer Relationship Management)
- **Location**: `/var/www/tradifyerp/TradifyERP/crm/`
- **Files**: `models.py`, `views.py`, `urls.py`, `admin.py`, `forms.py`, `retail_forms.py`, `retail_models.py`, `apps.py`
- **Purpose**: Customer data, lead management, sales opportunities, retail customer tracking
- **Dependencies**: Django, Django REST Framework

### 2. **Accounting** (General Ledger & Financial)
- **Location**: `/var/www/tradifyerp/TradifyERP/accounting/`
- **Files**: `models.py`, `views.py`, `urls.py`, `admin.py`, `forms.py`, `apps.py`
- **Purpose**: Chart of Accounts, Journal Entries, GL Reports, Trial Balance, P&L, Balance Sheet
- **Dependencies**: Django, PostgreSQL, Audit Logging module

### 3. **AP** (Accounts Payable)
- **Location**: `/var/www/tradifyerp/TradifyERP/ap/`
- **Files**: `models.py`, `views.py`, `urls.py`, `admin.py`, `forms.py`, `apps.py`
- **Purpose**: Vendor management, bill processing, payment scheduling, expense tracking
- **Dependencies**: Django, Accounting module

### 4. **AR** (Accounts Receivable)
- **Location**: `/var/www/tradifyerp/TradifyERP/ar/`
- **Files**: `models.py`, `views.py`, `urls.py`, `admin.py`, `forms.py`, `apps.py`
- **Purpose**: Customer invoices, payment collection, aging reports, credit management
- **Dependencies**: Django, Accounting module

### 5. **Cash Management**
- **Location**: `/var/www/tradifyerp/TradifyERP/cash_management/`
- **Files**: `models.py`, `views.py`, `urls.py`, `admin.py`, `forms.py`, `apps.py`
- **Purpose**: Cash accounts, liquidity management, bank reconciliation, cash transfers
- **Dependencies**: Django, Accounting module

### 6. **Audit Logging**
- **Location**: `/var/www/tradifyerp/TradifyERP/audit_logging/`
- **Files**: `models.py`, `admin.py`, `apps.py`
- **Purpose**: Track all user activities, data changes, audit trail, compliance logging
- **Dependencies**: Django

### 7. **TradifyERP** (Main Project)
- **Location**: `/var/www/tradifyerp/TradifyERP/`
- **Files**: `settings_production.py`, `wsgi.py`, `__init__.py`, `apps.py`
- **Purpose**: Main Django project configuration, URL routing, WSGI entry point
- **Dependencies**: All modules above

---

## 🐍 PYTHON PACKAGES (39 Total)

### Framework & Server
```
Django==5.2.9
djangorestframework==3.14.0
gunicorn==23.0.0
asgiref==3.11.0
wsgiref (built-in)
```

### Database & ORM
```
psycopg2-binary==2.9.9 (PostgreSQL driver)
sqlparse==0.5.4
```

### Authentication & Security
```
django-allauth==65.13.1
social-auth-app-django==5.6.0
social-auth-core==4.8.1
django-otp==1.1.3
django-ratelimit==4.1.0
PyJWT==2.10.1
oauthlib==3.3.1
python3-openid==3.2.0
requests-oauthlib==2.0.0
cryptography==41.0.0
```

### Frontend & Templates
```
crispy-bootstrap5==2025.6
django-crispy-forms==2.5
pillow==11.0.0
```

### Data Handling
```
django-import-export==4.3.14
openpyxl==3.1.5
tablib==3.9.0
defusedxml==0.7.1
diff-match-patch==20241021
```

### API & HTTP
```
requests==2.32.5
django-cors-headers==4.3.0
certifi==2025.11.12
charset-normalizer==3.4.4
idna==3.11
urllib3==2.6.2
```

### Caching & Sessions
```
django-redis==5.4.0
redis==7.1.0
```

### Utilities & Extensions
```
django-extensions==4.1
python-decouple==3.8
pytz==2025.2
packaging==25.0
cffi==2.0.0
pycparser==2.23
et_xmlfile==2.0.0
```

---

## 🖥️ SYSTEM COMPONENTS

### Web Server
```
Nginx (reverse proxy)
- Port: 80/443
- Location: /etc/nginx/
- Service: nginx.service
```

### Application Server
```
Gunicorn (WSGI application server)
- Version: 23.0.0
- Workers: 5
- Port: 127.0.0.1:8000
- Service: gunicorn.service
- Timeout: 300 seconds
```

### Database Server
```
PostgreSQL 16.13
- Host: 192.168.20.11
- Port: 5432
- Database: tradifyerp_db
- User: zubair
- Data Directory: /var/lib/postgresql/16/
```

### Cache Server (Configured)
```
Redis
- Used by: django-redis
- Purpose: Session caching, cache framework
```

---

## 📂 DIRECTORY STRUCTURE

```
APP SERVER: /var/www/tradifyerp/
├── TradifyERP/                 (Django project root)
│   ├── crm/                    (CRM module)
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── forms.py
│   │   ├── retail_forms.py
│   │   └── retail_models.py
│   ├── accounting/             (Accounting module)
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── forms.py
│   ├── ap/                     (Accounts Payable)
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── forms.py
│   ├── ar/                     (Accounts Receivable)
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── forms.py
│   ├── cash_management/        (Cash Management)
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── forms.py
│   ├── audit_logging/          (Audit Logging)
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   └── models.py
│   ├── settings_production.py  (Production settings)
│   ├── wsgi.py                 (WSGI entry point)
│   └── [utility scripts]
├── venv/                       (Python virtual environment)
│   └── bin/
│       ├── gunicorn
│       └── pip
└── [Other Django stuff]

DB SERVER: /var/lib/postgresql/16/
├── main/                       (PostgreSQL cluster data)
├── wal/                        (Write-ahead logs)
└── pg_wal/                     (WAL files)

DB SERVER: /usr/lib/postgresql/16/
├── bin/                        (PostgreSQL tools)
│   ├── pg_dump
│   ├── pg_restore
│   ├── pg_basebackup
│   └── psql
└── lib/                        (PostgreSQL libraries)
```

---

## 🔌 EXTERNAL INTEGRATIONS

| Integration | Purpose | Status |
|-------------|---------|--------|
| OAuth2 | Third-party authentication | Configured |
| Social Auth | Social media login (Google, Facebook, etc.) | Configured |
| Email | Email notifications | Not detected |
| Webhooks | External event handling | Not detected |
| API Keys | REST API authentication | Configured (JWT) |
| Two-Factor Auth (OTP) | Enhanced security | Installed |

---

## 📊 TECHNOLOGY SUMMARY TABLE

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| **Language** | Python | 3.12.3 | Application development |
| **Framework** | Django | 5.2.9 | Web framework |
| **REST API** | Django REST Framework | 3.14.0 | REST API implementation |
| **Web Server** | Nginx | Latest | Reverse proxy, static files |
| **App Server** | Gunicorn | 23.0.0 | WSGI server |
| **Database** | PostgreSQL | 16.13 | Relational database |
| **Cache** | Redis | Latest | Session/cache storage |
| **Authentication** | django-allauth | 65.13.1 | Authentication system |
| **Authorization** | OAuth2/OTP | 3.2.0 / 1.1.3 | Authorization & 2FA |
| **Frontend** | Bootstrap 5 | Latest | UI framework |

---

## 🎯 MODULE DEPENDENCIES

```
crm ────────┐
            ├─→ Accounting ┐
ap ─────────┤             ├─→ [Database: tradifyerp_db]
ar ─────────┤             │
cash_mgmt ──┘             ├─→ Audit Logging
            
All modules depend on:
- Django 5.2.9
- PostgreSQL 16.13
- Django REST Framework 3.14.0
```

---

## 🔐 Security Features Installed

1. ✅ **Authentication**
   - django-allauth (local + social auth)
   - OAuth2
   - JWT tokens
   - Social auth core

2. ✅ **Authorization**
   - Django permission system
   - Rate limiting (4.1.0)
   - CORS support

3. ✅ **Data Security**
   - SSL/TLS via Nginx
   - Password hashing
   - Defused XML (XXE prevention)

4. ✅ **Audit & Compliance**
   - Comprehensive audit logging
   - Two-factor authentication (OTP)
   - OpenID support

5. ✅ **Transport Security**
   - HTTPS via Nginx
   - Encrypted database connections
   - SSH key-based server access

---

## 📈 Scalability Components

- ✅ **Multi-worker app server** (5 Gunicorn workers)
- ✅ **Database connection pooling** (via psycopg2)
- ✅ **Redis caching** (distributed cache)
- ✅ **Modular Django apps** (can be deployed separately)
- ✅ **REST API** (allows distributed clients)
- ⚠️ **Load balancing** (not configured)
- ⚠️ **Database replication** (not configured)

---

**Generated**: April 7, 2026 | **Servers**: 2 | **Modules**: 7 | **Python Packages**: 39+
