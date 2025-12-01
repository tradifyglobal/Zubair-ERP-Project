# Manufacturing Module - Quick Reference Guide

## New Models Overview

### 1. Workstation
```python
# Physical machines/workstations on the plant floor
Workstation(
    workstation_code="WS-001",  # Unique identifier
    workstation_name="CNC Machine 1",
    workstation_type="CNC",  # Type: CNC, Assembly, Testing, etc.
    capacity_per_hour=10.5,  # Units per hour
    plant_floor_section="Section A",
    status="ACTIVE",  # ACTIVE, MAINTENANCE, INACTIVE
    hourly_rate=50.00
)
```

### 2. Operation
```python
# Manufacturing operations performed at workstations
Operation(
    operation_code="OP-001",  # Unique identifier
    operation_name="Turning",
    workstation=workstation,  # FK to Workstation
    standard_time_minutes=15.5,  # Time per unit
    cost_per_unit=25.00
)
```

### 3. StockEntry
```python
# Track all stock movements
StockEntry(
    entry_id="SE-ABC123",  # Auto-generated
    entry_type="INWARD",  # INWARD, OUTWARD, TRANSFER, PRODUCTION, SCRAP, ADJUSTMENT
    item=raw_material,  # FK to RawMaterial
    quantity=100.00,
    unit_cost=5.00,
    source_warehouse="Main",
    destination_warehouse="Floor",
    reference_type="PurchaseOrder",  # Reference tracking
    reference_id=123
)
```

### 4. JobCard
```python
# Production floor work instructions
JobCard(
    job_card_id="JC-XYZ789",  # Auto-generated
    production_order=po,  # FK to ProductionOrder
    operation=operation,  # FK to Operation
    workstation=workstation,  # FK to Workstation
    assigned_to=user,  # Who is assigned
    status="IN_PROGRESS",  # DRAFT, RELEASED, IN_PROGRESS, COMPLETED, REJECTED
    quantity_to_produce=100.00,
    quantity_produced=85.00,
    quantity_rejected=2.00,
    # Methods:
    # .get_progress_percentage() -> returns % complete
)
```

### 5. DowntimeEntry
```python
# Track production downtime
DowntimeEntry(
    downtime_id="DT-123ABC",  # Auto-generated
    job_card=job_card,  # FK to JobCard
    workstation=workstation,  # FK to Workstation
    downtime_reason="MACHINE_BREAKDOWN",  # Predefined reasons
    start_time=datetime.now(),
    end_time=datetime.now() + timedelta(hours=2),
    duration_minutes=120,  # Auto-calculated
    description="Spindle bearing failure",
    corrective_action="Replaced bearing"
)
```

---

## URL Endpoints

### Workstations
```
GET  /manufacturing/workstations/              # List workstations
POST /manufacturing/workstations/new/          # Create workstation
POST /manufacturing/workstations/<id>/delete/  # Delete workstation
```

### Operations
```
GET  /manufacturing/operations/                # List operations
POST /manufacturing/operations/new/            # Create operation
POST /manufacturing/operations/<id>/delete/    # Delete operation
```

### Stock Entries
```
GET  /manufacturing/stock-entries/             # List stock entries
POST /manufacturing/stock-entries/new/         # Create entry
POST /manufacturing/stock-entries/<id>/delete/ # Delete entry
```

### Job Cards
```
GET    /manufacturing/job-cards/               # List job cards (with status filter)
POST   /manufacturing/job-cards/new/           # Create job card
POST   /manufacturing/job-cards/<id>/edit/     # Update job card
DELETE /manufacturing/job-cards/<id>/delete/   # Delete job card
```

### Downtime Entries
```
GET  /manufacturing/downtime-entries/              # List (with reason filter)
POST /manufacturing/downtime-entries/new/          # Create entry
POST /manufacturing/downtime-entries/<id>/delete/  # Delete entry
```

### Reports
```
GET /manufacturing/reports/bom-stock/          # BOM Stock Report
GET /manufacturing/reports/production-plan/    # Production Planning Report
GET /manufacturing/reports/plant-floor/        # Plant Floor (Real-time)
GET /manufacturing/reports/forecasting/        # Forecasting
```

### Tools
```
GET /manufacturing/tools/bom-update/       # BOM Update Tool
GET /manufacturing/tools/bom-comparison/   # BOM Comparison Tool
```

---

## View Classes

### Create/Read/Update/Delete

| Model | List View | Create View | Update View | Delete View |
|-------|-----------|-------------|-------------|------------|
| Workstation | ✅ | ✅ | - | ✅ |
| Operation | ✅ | ✅ | - | ✅ |
| StockEntry | ✅ | ✅ | - | ✅ |
| JobCard | ✅ | ✅ | ✅ | ✅ |
| DowntimeEntry | ✅ | ✅ | - | ✅ |

### Reports & Tools

| Name | Class | Purpose |
|------|-------|---------|
| BOM Stock Report | BOMStockReportView | Stock levels per BOM |
| Production Plan Report | ProductionPlanReportView | Order statistics |
| Plant Floor | PlantFloorView | Real-time workstation status |
| Forecasting | ForecastingView | Production demand vs. capacity |
| BOM Update Tool | BOMUpdateToolView | Bulk BOM modifications |
| BOM Comparison Tool | BOMComparisonToolView | Compare two BOMs |

---

## Database Schema

### Workstation Table
```sql
-- manufacturing_workstation
- id (PK)
- entity_id (FK to accounting.Entity)
- workstation_code (UNIQUE)
- workstation_name
- workstation_type
- capacity_per_hour (DECIMAL)
- plant_floor_section
- status (VARCHAR: ACTIVE, MAINTENANCE, INACTIVE)
- hourly_rate (DECIMAL)
- is_active (BOOLEAN)
- created_at, updated_at
```

### Operation Table
```sql
-- manufacturing_operation
- id (PK)
- entity_id (FK)
- operation_code (UNIQUE)
- operation_name
- description
- workstation_id (FK, nullable)
- standard_time_minutes (DECIMAL)
- cost_per_unit (DECIMAL)
- is_active (BOOLEAN)
- created_at, updated_at
```

### StockEntry Table
```sql
-- manufacturing_stock_entry
- id (PK)
- entity_id (FK)
- entry_id (UNIQUE)
- entry_type (VARCHAR)
- entry_date (DATETIME)
- source_warehouse
- destination_warehouse
- item_id (FK to RawMaterial)
- quantity (DECIMAL)
- unit_cost (DECIMAL)
- reference_type
- reference_id
- remarks
- created_by_id (FK to User)
- created_at, updated_at
-- INDEX: (entry_date, entry_type), (item_id, entry_date)
```

### JobCard Table
```sql
-- manufacturing_job_card
- id (PK)
- entity_id (FK)
- job_card_id (UNIQUE)
- production_order_id (FK)
- operation_id (FK, nullable)
- workstation_id (FK, nullable)
- assigned_to_id (FK to User, nullable)
- status (VARCHAR)
- scheduled_start_date (DATETIME)
- scheduled_end_date (DATETIME)
- actual_start_date (DATETIME, nullable)
- actual_end_date (DATETIME, nullable)
- quantity_to_produce (DECIMAL)
- quantity_produced (DECIMAL)
- quantity_rejected (DECIMAL)
- instructions, remarks
- created_at, updated_at
-- INDEX: (production_order_id, status), (workstation_id, status)
```

### DowntimeEntry Table
```sql
-- manufacturing_downtime_entry
- id (PK)
- entity_id (FK)
- downtime_id (UNIQUE)
- job_card_id (FK)
- workstation_id (FK, nullable)
- downtime_reason (VARCHAR)
- start_time (DATETIME)
- end_time (DATETIME)
- duration_minutes (INTEGER)
- description, corrective_action
- created_by_id (FK to User)
- created_at
-- INDEX: (workstation_id, start_time), (job_card_id, start_time)
```

---

## Common Use Cases

### 1. Create Production Flow
```python
# 1. Create workstation
workstation = Workstation.objects.create(
    workstation_code="WS-001",
    workstation_name="CNC Machine",
    capacity_per_hour=10
)

# 2. Create operation
operation = Operation.objects.create(
    operation_code="OP-001",
    workstation=workstation,
    standard_time_minutes=15
)

# 3. Assign to production order via job card
job_card = JobCard.objects.create(
    production_order=production_order,
    operation=operation,
    workstation=workstation,
    quantity_to_produce=100
)

# 4. Log downtime if needed
DowntimeEntry.objects.create(
    job_card=job_card,
    workstation=workstation,
    downtime_reason="MACHINE_BREAKDOWN",
    start_time=timezone.now(),
    end_time=timezone.now() + timedelta(hours=2),
    description="Spindle failure"
)
```

### 2. Track Stock Movement
```python
# Receive raw material
StockEntry.objects.create(
    entry_type="INWARD",
    item=raw_material,
    quantity=500,
    unit_cost=10.00,
    source_warehouse="Supplier",
    destination_warehouse="Main"
)

# Issue to production
StockEntry.objects.create(
    entry_type="OUTWARD",
    item=raw_material,
    quantity=100,
    unit_cost=10.00,
    source_warehouse="Main",
    destination_warehouse="Production Floor",
    reference_type="ProductionOrder",
    reference_id=production_order.id
)
```

### 3. Monitor Production Progress
```python
job_card = JobCard.objects.get(id=1)

# Update production quantities
job_card.quantity_produced = 85
job_card.quantity_rejected = 2
job_card.save()

# Get progress percentage
progress = job_card.get_progress_percentage()  # Returns 85
```

### 4. Generate Reports
```python
# Get workstation status
from manufacturing.views import PlantFloorView

view = PlantFloorView()
context = view.get_context_data()
workstations = context['workstations']  # List of workstation data with status
active_count = context['active_workstations']
```

---

## Permissions

### Required for CRUD Operations
- **Create:** `manufacturing.add_<model>`
- **Read:** `manufacturing.view_<model>` (automatic via ListView)
- **Update:** `manufacturing.change_<model>`
- **Delete:** Requires `module_permission_required("manufacturing", "delete")`

### Views Protected By
- `LoginRequiredMixin` - All views
- `CSRF protection` - All POST/DELETE views
- `Entity filtering` - Multi-tenant isolation
- `Permission decorator` - Delete operations

---

## Search & Filtering

### Workstation List
- Search by: `workstation_name`, `workstation_code`

### Operation List
- Search by: `operation_name`, `operation_code`

### StockEntry List
- Search by: `entry_id`, `item.material_name`
- Filter by: `entry_type`

### JobCard List
- Filter by: `status` (DRAFT, RELEASED, IN_PROGRESS, COMPLETED, REJECTED)

### DowntimeEntry List
- Filter by: `downtime_reason`

---

## Best Practices

### 1. **Workstation Setup**
- Use descriptive codes (WS-001, WS-PAINT, etc.)
- Set realistic capacity figures
- Update status when maintenance occurs
- Track hourly rates for costing

### 2. **Operation Management**
- Link operations to workstations
- Set accurate standard times
- Include operation costs for costing analysis
- Keep operation codes consistent across BOMs

### 3. **Job Card Workflow**
- Create from ProductionOrder
- Release before production starts
- Track actual start/end dates
- Record all rejections immediately
- Use for full traceability

### 4. **Downtime Tracking**
- Log immediately when downtime starts
- Use specific categories
- Always record corrective actions
- Review for continuous improvement

### 5. **Stock Entry**
- Use entry type correctly
- Always link to reference document
- Record unit cost for costing
- Track warehouse locations

---

## Performance Tips

1. **Indexes Used:**
   - JobCard: (production_order, status), (workstation, status)
   - DowntimeEntry: (workstation, start_time), (job_card, start_time)
   - StockEntry: (entry_date, entry_type), (item, entry_date)

2. **Query Optimization:**
   - Use `select_related()` for ForeignKeys
   - Use `prefetch_related()` for reverse FK
   - Filter by entity first
   - Paginate large lists (25 per page)

3. **Pagination:**
   - All list views: 25 items per page
   - Reduces memory usage
   - Improves page load time

---

## Integration Points

### With Other Modules

- **Accounting:** Operation costs → GL posting
- **CRM:** Production orders from sales
- **Inventory:** Stock entries affect inventory levels
- **HR:** Job card assignments to workers

### Data Flow
```
Sales Order (CRM)
  ↓
Production Order (Manufacturing)
  ↓
Job Card (Manufacturing - NEW)
  ↓
Workstation Execution (Manufacturing - NEW)
  ↓
Stock Entry (Manufacturing - NEW) / Cost GL Posting (Accounting)
```

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Empty job cards list | No job cards created | Create via ProductionOrder |
| Downtime not showing | Wrong workstation | Ensure job_card workstation matches |
| Stock entry rejected | Missing item | Select valid RawMaterial |
| Low report numbers | Entity filtering | Check user entity permissions |
| Slow list views | Too many records | Use filters, pagination |

---

**Last Updated:** November 23, 2025  
**Status:** Production Ready ✅
