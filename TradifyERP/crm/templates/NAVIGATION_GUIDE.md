# Where to Find All New CRM Modules

## Navigation Access

The new CRM modules are accessible from the **CRM** menu in the top navigation bar:

**Path:** `CRM` → (See categories below)

---

## 📊 Complete Module Directory

### 1. **MASTERS** (Core Data Management)
Located in: `CRM → Masters`

| Module | URL | Description |
|--------|-----|-------------|
| **Territories** | `/crm/territories/` | Manage sales territories and regional assignments |
| **Customer Groups** | `/crm/customer-groups/` | Segment and categorize customers |
| **Contacts** | `/crm/contacts/` | Store contact information and relationships |
| **Prospects** | `/crm/prospects/` | Track potential sales opportunities |
| **Sales People** | `/crm/salespersons/` | Manage sales team members |
| **Lead Sources** | `/crm/lead-sources/` | Categorize and track lead origins |

---

### 2. **SALES PIPELINE** (Transaction Management)
Located in: `CRM → Sales Pipeline`

| Module | URL | Description |
|--------|-----|-------------|
| **Contracts** | `/crm/contracts/` | Manage sales contracts and agreements |
| **Appointments** | `/crm/appointments/` | Schedule and track meetings |
| **Communications** | `/crm/communications/` | Log all communication activities |

---

### 3. **EMAIL & SMS** (Campaign Management)
Located in: `CRM → Email & SMS`

| Module | URL | Description |
|--------|-----|-------------|
| **Email Campaigns** | `/crm/email-campaigns/` | Create and manage email marketing campaigns |
| **SMS Campaigns** | `/crm/sms-campaigns/` | Send and track SMS communications |
| **Email Groups** | `/crm/email-groups/` | Manage email distribution lists |

---

### 4. **MAINTENANCE** (Service Management)
Located in: `CRM → Maintenance`

| Module | URL | Description |
|--------|-----|-------------|
| **Maintenance Schedules** | `/crm/maintenance-schedules/` | Plan preventive maintenance |
| **Maintenance Visits** | `/crm/maintenance-visits/` | Record service visit details |
| **Warranty Claims** | `/crm/warranty-claims/` | Manage warranty claim tracking |

---

## 🎯 Quick Navigation Reference

### From the CRM Dropdown Menu:

```
CRM (Main Menu)
├── Dashboard
│   └── CRM Dashboard
├── Lead Management
│   └── All Leads
├── Opportunities
│   └── All Opportunities
├── Quotes
│   └── All Quotes
├── Activities
│   └── All Activities
├── Campaigns
│   └── All Campaigns
├── Masters ⭐ (NEW)
│   ├── Territories
│   ├── Customer Groups
│   ├── Contacts
│   ├── Prospects
│   ├── Sales People
│   └── Lead Sources
├── Sales Pipeline ⭐ (NEW)
│   ├── Contracts
│   ├── Appointments
│   └── Communications
├── Email & SMS ⭐ (NEW)
│   ├── Email Campaigns
│   ├── SMS Campaigns
│   └── Email Groups
└── Maintenance ⭐ (NEW)
    ├── Maintenance Schedules
    ├── Maintenance Visits
    └── Warranty Claims
```

---

## 🚀 Features Available in Each Module

### ✅ List View Features
- Responsive table display
- Pagination (20 items per page)
- View/Edit/Delete buttons for each record
- Status indicators and badges
- Empty state messaging
- Date formatting

### ✅ Quick Actions
- **View** (Eye icon) - See full record details
- **Edit** (Edit icon) - Update record information
- **Delete** (Trash icon) - Remove record with confirmation

### ✅ Create New Records
- **"New [Module Name]"** button in top-right corner
- Links in the menu for quick access
- Comprehensive form with all required fields
- Bootstrap-styled forms with validation

---

## 🔗 Direct Links to Modules

**Copy and paste these URLs to access modules directly:**

### Masters
- http://localhost:8000/crm/territories/
- http://localhost:8000/crm/customer-groups/
- http://localhost:8000/crm/contacts/
- http://localhost:8000/crm/prospects/
- http://localhost:8000/crm/salespersons/
- http://localhost:8000/crm/lead-sources/

### Sales Pipeline
- http://localhost:8000/crm/contracts/
- http://localhost:8000/crm/appointments/
- http://localhost:8000/crm/communications/

### Email & SMS
- http://localhost:8000/crm/email-campaigns/
- http://localhost:8000/crm/sms-campaigns/
- http://localhost:8000/crm/email-groups/

### Maintenance
- http://localhost:8000/crm/maintenance-schedules/
- http://localhost:8000/crm/maintenance-visits/
- http://localhost:8000/crm/warranty-claims/

---

## 📋 Getting Started

### Step 1: Navigate to CRM
Click on **CRM** in the top navigation bar

### Step 2: Select Module Category
Choose from:
- Masters (data setup)
- Sales Pipeline (transactions)
- Email & SMS (campaigns)
- Maintenance (service)

### Step 3: View or Create Records
- **View** existing records in the list
- Click **"New [Module]"** button to create new record
- Use **Edit/Delete** buttons for record management

---

## 🎓 Typical Workflow

### For Sales Teams:
1. Set up **Territories** (region assignments)
2. Add **Sales People** (team members)
3. Create **Lead Sources** (where leads come from)
4. Track **Prospects** (potential customers)
5. Manage **Contracts** (sales agreements)
6. Schedule **Appointments** (customer meetings)
7. Log **Communications** (all interactions)

### For Support Teams:
1. Create **Maintenance Schedules** (preventive service)
2. Record **Maintenance Visits** (service completion)
3. Track **Warranty Claims** (customer claims)
4. Create **Appointments** (service scheduling)

### For Marketing Teams:
1. Create **Email Groups** (distribution lists)
2. Send **Email Campaigns** (marketing messages)
3. Send **SMS Campaigns** (text marketing)
4. Track **Communications** (engagement)

---

## 📊 Module Relationships

```
Territory
├── Sales People (assigned to territory)
│   ├── Appointments (schedules)
│   ├── Communications (activity log)
│   └── Contracts (sales agreements)

Customer Group
├── Contacts (group members)
│   ├── Appointments (interactions)
│   └── Communications (history)

Prospects
├── Appointments (follow-ups)
├── Communications (engagement)
└── Contracts (conversion)

Lead Sources
└── Prospects (where prospects came from)

Email/SMS Campaigns
├── Email Groups (recipients)
├── Communications (tracking)
└── Contacts (audience)

Maintenance
├── Maintenance Schedules (plans)
├── Maintenance Visits (execution)
└── Warranty Claims (follow-up)
```

---

## ⚙️ System Status

✅ **16 new models** created and operational
✅ **16 list templates** deployed and ready
✅ **60+ CRUD operations** available
✅ **Navigation menu** updated with all modules
✅ **All forms** configured with validation
✅ **Database** migrations applied successfully

---

## 🆘 Troubleshooting

If modules don't appear in the menu:
1. Verify user has CRM module permissions
2. Check user is logged in
3. Refresh the browser
4. Clear browser cache

If you see "404 Not Found":
1. Verify URL spelling
2. Check Django development server is running
3. Run `python manage.py check` to verify no errors
4. Check URL patterns in `crm/urls.py`

---

## 📞 Additional Resources

**For more information:**
- View all models: Admin Panel → CRM section
- Database queries: Django ORM documentation
- Template customization: Edit HTML files in `crm/templates/crm/`
- Form customization: Edit Python files in `crm/forms.py`

