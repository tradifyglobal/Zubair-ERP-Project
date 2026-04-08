# TradifyERP - Complete Modules & Apps List

**Last Updated**: April 7, 2026  
**Total Django Modules**: 14 ERP Modules + Admin Modules

---

## 🎯 CORE ERP MODULES (14 Total)

### 1. **Accounting** 
   - **Location**: `/var/www/tradifyerp/accounting/`
   - **Purpose**: General Ledger, Chart of Accounts, Journal Entries, Financial Reporting
   - **Features**: GL Reports, Trial Balance, P&L, Balance Sheet
   - **Status**: ✅ Active

### 2. **Shareholder**
   - **Location**: `/var/www/tradifyerp/shareholder/`
   - **Purpose**: Shareholder management, capital contributions, dividend tracking
   - **Features**: Shareholder registry, capital contribution workflows, equity tracking
   - **Status**: ✅ Active

### 3. **HR** (Human Resources)
   - **Location**: `/var/www/tradifyerp/hr/`
   - **Purpose**: Employee management, payroll, attendance tracking
   - **Features**: Employee records, salary management, leave management, performance tracking
   - **Status**: ✅ Active

### 4. **Manufacturing**
   - **Location**: `/var/www/tradifyerp/manufacturing/`
   - **Purpose**: Production planning, work orders, bill of materials
   - **Features**: BOM management, production orders, shop floor tracking, manufacturing costs
   - **Status**: ✅ Active

### 5. **Sales**
   - **Location**: `/var/www/tradifyerp/sales/`
   - **Purpose**: Sales order management, quotations, sales analysis
   - **Features**: Sales orders, quotations, sales invoicing, commission tracking
   - **Status**: ✅ Active

### 6. **Inventory**
   - **Location**: `/var/www/tradifyerp/inventory/`
   - **Purpose**: Stock management, warehouse operations, inventory valuation
   - **Features**: Stock levels, inventory adjustments, item tracking, warehouse management
   - **Status**: ✅ Active

### 7. **AP** (Accounts Payable)
   - **Location**: `/var/www/tradifyerp/ap/`
   - **Purpose**: Vendor bill management, payment processing, expense tracking
   - **Features**: Vendor bills, payment scheduling, vendor management, expense reconciliation
   - **Status**: ✅ Active

### 8. **Procurement**
   - **Location**: `/var/www/tradifyerp/procurement/`
   - **Purpose**: Purchase order management, vendor selection, procurement workflow
   - **Features**: Purchase orders, RFQ (Request for Quote), vendor management, procurement analytics
   - **Status**: ✅ Active

### 9. **Cash Management**
   - **Location**: `/var/www/tradifyerp/cash_management/`
   - **Purpose**: Cash flow management, liquidity planning, bank reconciliation
   - **Features**: Cash accounts, cash transfers, bank reconciliation, cash forecasting
   - **Status**: ✅ Active

### 10. **Projects**
   - **Location**: `/var/www/tradifyerp/projects/`
   - **Purpose**: Project management, task tracking, resource allocation
   - **Features**: Project planning, task management, resource allocation, project costing
   - **Status**: ✅ Active

### 11. **CRM** (Customer Relationship Management)
   - **Location**: `/var/www/tradifyerp/crm/`
   - **Purpose**: Customer management, lead tracking, sales opportunities
   - **Features**: Customer profiles, lead management, opportunity tracking, customer interactions
   - **Status**: ✅ Active

### 12. **AR** (Accounts Receivable)
   - **Location**: `/var/www/tradifyerp/ar/`
   - **Purpose**: Customer invoice management, payment collection, aging reports
   - **Features**: Sales invoices, credit management, collection tracking, aging analysis
   - **Status**: ✅ Active

### 13. **Expenses**
   - **Location**: `/var/www/tradifyerp/expenses/`
   - **Purpose**: Employee expense tracking and reimbursement
   - **Features**: Expense reports, reimbursement workflows, expense categorization, approval workflows
   - **Status**: ✅ Active

### 14. **Maintenance**
   - **Location**: `/var/www/tradifyerp/maintenance/`
   - **Purpose**: Asset maintenance, preventive maintenance, maintenance requests
   - **Features**: Asset management, maintenance scheduling, work orders, preventive maintenance planning
   - **Status**: ✅ Active

---

## 🔧 UTILITY & ADMIN MODULES (4 Total)

### 1. **Minia**
   - **Location**: `/var/www/tradifyerp/minia/`
   - **Purpose**: Admin theme and dashboard UI framework
   - **Features**: Dashboard templates, responsive admin interface, theme assets
   - **Status**: ✅ Active

### 2. **Pages**
   - **Location**: `/var/www/tradifyerp/pages/`
   - **Purpose**: Static pages and content management
   - **Features**: Page creation, content management, URL routing for static content
   - **Status**: ✅ Active

### 3. **Apps**
   - **Location**: `/var/www/tradifyerp/apps/`
   - **Purpose**: Application configuration and app-level settings
   - **Features**: App configuration, settings management, global configs
   - **Status**: ✅ Active

### 4. **TradifyERP** (Main Project)
   - **Location**: `/var/www/tradifyerp/TradifyERP/`
   - **Purpose**: Main Django project configuration
   - **Features**: Settings files, URL routing, WSGI configuration
   - **Status**: ✅ Active

---

## 📦 DJANGO & THIRD-PARTY INTEGRATIONS

### Built-in Django Modules
- `django.contrib.admin` - Admin interface
- `django.contrib.auth` - Authentication & permissions
- `django.contrib.contenttypes` - Content type framework
- `django.contrib.sessions` - Session management
- `django.contrib.messages` - Messaging framework
- `django.contrib.staticfiles` - Static files management
- `django.contrib.sites` - Multi-site framework

### Authentication & Authorization
- `allauth` - Authentication system
- `allauth.account` - Account management
- `allauth.socialaccount` - Social media authentication
- `social_django` - Social authentication
- `django_otp` - Two-factor authentication (TOTP)
- `django_otp.plugins.otp_totp` - Time-based OTP

### API & Frontend
- `rest_framework` - Django REST Framework
- `crispy_forms` - Form rendering
- `crispy_bootstrap5` - Bootstrap 5 integration

### Security
- `corsheaders` - CORS support
- `django_ratelimit` - Rate limiting

---

## 📊 MODULES SUMMARY TABLE

| # | Module | Type | Purpose | Status |
|---|--------|------|---------|--------|
| 1 | Accounting | ERP | General Ledger & Financial Reports | ✅ Active |
| 2 | Shareholder | ERP | Shareholder Management | ✅ Active |
| 3 | HR | ERP | Human Resources & Payroll | ✅ Active |
| 4 | Manufacturing | ERP | Production Planning & Orders | ✅ Active |
| 5 | Sales | ERP | Sales Orders & Quotations | ✅ Active |
| 6 | Inventory | ERP | Stock & Warehouse Management | ✅ Active |
| 7 | AP | ERP | Accounts Payable | ✅ Active |
| 8 | Procurement | ERP | Purchase Orders & Vendor Management | ✅ Active |
| 9 | Cash Management | ERP | Cash Flow & Liquidity | ✅ Active |
| 10 | Projects | ERP | Project Management | ✅ Active |
| 11 | CRM | ERP | Customer Relationship Management | ✅ Active |
| 12 | AR | ERP | Accounts Receivable | ✅ Active |
| 13 | Expenses | ERP | Employee Expenses & Reimbursement | ✅ Active |
| 14 | Maintenance | ERP | Asset Maintenance | ✅ Active |
| 15 | Minia | Admin | Dashboard & UI Theme | ✅ Active |
| 16 | Pages | Utility | Static Pages & Content | ✅ Active |
| 17 | Apps | Utility | App Configuration | ✅ Active |
| 18 | TradifyERP | Project | Main Django Project | ✅ Active |

---

## 🔄 MODULE DEPENDENCIES & RELATIONSHIPS

```
┌─────────────────────────────────────────┐
│           CRM Module                    │
│    (Customer Management)                │
└────────────┬────────────────────────────┘
             │
     ┌───────┴───────┐
     │               │
┌────▼────┐  ┌──────▼──────┐
│ Sales   │  │ Projects    │
│ Module  │  │ Module      │
└────┬────┘  └──────┬──────┘
     │              │
     └───────┬──────┘
             │
      ┌──────▼──────┐
      │ Inventory   │
      │ & Procure   │
      │ Module      │
      └──────┬──────┘
             │
    ┌────────┴────────┐
    │                 │
┌───▼──┐         ┌───▼─────────┐
│  AP  │         │Manufacturing│
│(Purch)         │   Module    │
└───┬──┘         └───┬─────────┘
    │                │
    └────────┬───────┘
             │
    ┌────────▼────────┐
    │  Accounting     │
    │  (GL Module)    │
    └────────┬────────┘
             │
    ┌────────┴──────────┐
    │                   │
 ┌──▼──┐          ┌────▼─────┐
 │ AR  │          │ Cash      │
 │Recv │          │Management │
 └──┬──┘          └────┬──────┘
    │                  │
    └──────────┬───────┘
               │
    ┌──────────▼─────────┐
    │ Shareholder Module │
    │ (Capital Contrib)  │
    └────────────────────┘

Other Modules: HR, Expenses, Maintenance, Audit Logging
```

---

## 📁 DIRECTORY STRUCTURE

```
/var/www/tradifyerp/
├── TradifyERP/              (Main Django Project)
│   ├── settings_production.py
│   ├── wsgi.py
│   └── urls.py
│
├── ERP MODULES:
├── accounting/
├── shareholder/
├── hr/
├── manufacturing/
├── sales/
├── inventory/
├── ap/
├── procurement/
├── cash_management/
├── projects/
├── crm/
├── ar/
├── expenses/
└── maintenance/
│
├── UTILITY MODULES:
├── minia/                   (Dashboard UI)
├── pages/                   (Static Pages)
├── apps/                    (App Config)
│
├── INFRASTRUCTURE:
├── venv/                    (Python Virtual Environment)
├── templates/               (HTML Templates)
├── static/                  (Static Files: CSS, JS, Images)
├── staticfiles/             (Collected Static Files)
├── media/                   (User Uploads)
├── logs/                    (Application Logs)
├── backups/                 (Database Backups)
└── manage.py               (Django Management Command)
```

---

## 🚀 KEY FEATURES BY MODULE

### Finance Modules (Accounting, AP, AR, Cash Management)
- Complete double-entry accounting system
- Multi-currency support
- Financial reporting (P&L, Balance Sheet, Trial Balance)
- Bank reconciliation
- Budget tracking and variance analysis

### Operations Modules (Sales, Procurement, Manufacturing, Inventory)
- Order-to-cash workflow (Sales)
- Procure-to-pay workflow (Procurement & AP)
- Manufacturing workflow (BOM, Work Orders, Production Planning)
- Real-time inventory tracking
- Warehouse management

### Management Modules (Projects, HR, Expenses, Maintenance)
- Project management and costing
- Employee management and payroll
- Expense tracking and reimbursement
- Asset maintenance and tracking

### Business Intelligence
- CRM for customer management
- Shareholder management for equity tracking
- Comprehensive audit logging
- Multi-user access control
- Role-based permissions

---

## 🔐 NOT INSTALLED

- **Audit Logging Module** - Configured but disabled in INSTALLED_APPS
  - Can be enabled for comprehensive audit trail functionality
  - Comment out the line: `# 'audit_logging.apps.AuditLoggingConfig'`

---

## 📞 QUICK REFERENCE

### Access All Modules
```powershell
ssh root@192.168.20.10
cd /var/www/tradifyerp
ls -la    # View all modules
```

### Module Structure
Each module typically contains:
- `models.py` - Database models
- `views.py` - View logic
- `urls.py` - URL routing
- `admin.py` - Admin interface registration
- `forms.py` - HTML forms
- `apps.py` - App configuration
- `migrations/` - Database migrations
- `templates/` - HTML templates
- `management/commands/` - Custom management commands

### Run Migrations for Specific Module
```powershell
ssh root@192.168.20.10
cd /var/www/tradifyerp
python manage.py migrate shareholder
# Or for all modules
python manage.py migrate
```

---

**Total Modules**: 18 (14 ERP + 4 Admin/Utility)  
**Generated**: April 7, 2026  
**Framework**: Django 5.2.9 | Database: PostgreSQL 16.13
