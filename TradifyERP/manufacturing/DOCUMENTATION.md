"""
MANUFACTURING MODULE DOCUMENTATION
====================================

Complete Manufacturing Operations Management System
Following Industry Best Practices (ISO 9001, APICS CPIM standards)

TABLE OF CONTENTS
=================
1. Module Overview
2. Core Data Models
3. Business Processes
4. GL Integration
5. Multi-Entity Support
6. API Endpoints
7. Dashboard Metrics
8. Usage Examples
9. Best Practices


1. MODULE OVERVIEW
==================

The Manufacturing module provides comprehensive control of manufacturing operations including:

- PRODUCT MASTER DATA: Product catalog with BOM structure
- BILL OF MATERIALS (BOM): Component recipes with versioning
- PRODUCTION PLANNING: Work orders with status tracking
- SHOP FLOOR CONTROL: Production order execution and tracking
- QUALITY CONTROL: Inspection records and defect tracking
- EQUIPMENT MANAGEMENT: Asset tracking with maintenance scheduling
- COST ACCOUNTING: Labor and material cost absorption
- INVENTORY MANAGEMENT: Raw materials, WIP, finished goods


2. CORE DATA MODELS
===================

A. PRODUCT HIERARCHY
--------------------

ProductCategory
  - name: Category name (e.g., "Electronics", "Mechanical")
  - code: Unique code
  - revenue_account: GL account for revenue
  - cogs_account: GL account for COGS
  - is_active: Enable/disable category

Product (Finished Goods)
  - product_code: Unique SKU (e.g., "PROD-001")
  - name: Product name
  - category: Link to ProductCategory
  - is_manufactured: TRUE for make-to-order
  - manufacturing_lead_time: Days to produce
  - standard_batch_size: Standard lot size
  - standard_cost: Calculated from BOM
  - selling_price: Sales price
  - unit_of_measure: UNIT, KG, METER, etc.
  - inspection_level: NONE, BASIC, FULL, CERTIFIED
  - inventory_account: GL account for finished goods


B. BILL OF MATERIALS (BOM)
---------------------------

BillOfMaterials (Master)
  - product: Link to finished product
  - version: BOM version (1, 2, 3...)
  - effective_date: When this BOM becomes active
  - end_date: When BOM expires
  - approved_by: Engineering approval
  - approved_date: Approval timestamp

BOMLine (Components)
  - bom: Parent BOM
  - material: Link to RawMaterial
  - quantity_per_unit: How much material per unit
  - scrap_percentage: Waste allowance (0-100%)
  - unit_cost: Material cost
  - total_cost: With scrap factor = quantity * unit_cost * (1 + scrap%)


C. RAW MATERIALS & INVENTORY
-----------------------------

RawMaterial
  - material_code: Unique code (e.g., "MAT-001")
  - name: Material description
  - supplier: Vendor name
  - reorder_quantity: Purchase quantity
  - reorder_point: Trigger reorder
  - current_stock: On-hand quantity
  - standard_unit_cost: Cost for costing
  - inventory_account: GL account for raw materials


D. PRODUCTION ROUTING (Manufacturing Steps)
--------------------------------------------

Routing (Master)
  - product: Link to finished product
  - version: Routing version
  - effective_date: When active
  - approved_by: Approval

RoutingLine (Operations)
  - routing: Parent routing
  - work_center: Machine/department
  - sequence: Operation order (1, 2, 3...)
  - estimated_hours: Labor time
  - setup_hours: Setup time (not in total)
  - total_hours: estimated_hours + setup_hours


E. WORK CENTERS (Production Resources)
---------------------------------------

WorkCenter
  - code: Unique code (e.g., "WC-001")
  - name: Machine/department name
  - labor_cost_per_hour: Labor rate
  - machine_cost_per_hour: Overhead rate
  - total_hourly_cost: Sum of above
  - labor_expense_account: GL account
  - machine_expense_account: GL account


F. PRODUCTION ORDERS (Work Orders)
-----------------------------------

ProductionOrder
  - po_number: Unique order number (e.g., "PO-2024-001")
  - product: What to make
  - quantity_ordered: How many units
  - quantity_completed: Actual completed
  - quantity_scrapped: Defective units
  - start_date: When to start
  - due_date: When needed
  - completion_date: Actual completion
  - status: DRAFT → PLANNED → RELEASED → IN_PROGRESS → COMPLETE
  - bom: Which BOM to use
  - routing: Which routing to use
  - estimated_material_cost: From BOM
  - estimated_labor_cost: From routing
  - actual_material_cost: Actual incurred
  - actual_labor_cost: Actual incurred


G. QUALITY CONTROL
------------------

QualityInspection
  - production_order: Which PO
  - inspection_date: When inspected
  - quantity_inspected: How many units
  - status: PASS, FAIL, REWORK
  - defects_found: Description
  - defect_count: Number of defects
  - inspected_by: Quality inspector
  - notes: Comments


H. EQUIPMENT MANAGEMENT
-----------------------

Equipment
  - equipment_code: Unique code
  - name: Equipment name
  - model: Model number
  - serial_number: For tracking
  - acquisition_cost: Purchase price
  - acquisition_date: When purchased
  - status: OPERATIONAL, MAINTENANCE, REPAIR, RETIRED
  - last_maintenance_date: For scheduling
  - next_maintenance_date: Preventive maintenance
  - fixed_asset_account: GL account
  - depreciation_account: GL account


3. BUSINESS PROCESSES
=====================

A. PRODUCT SETUP PROCESS
-------------------------

1. Create ProductCategory
   - Set up revenue and COGS GL accounts
   
2. Create Product
   - Link to category
   - Set specifications, costs, pricing
   
3. Create BillOfMaterials (BOM)
   - Version 1, effective date, approval
   
4. Add BOMLine entries
   - Material, quantity, scrap %, unit cost
   - System calculates total cost including scrap
   
5. Create Routing
   - Version 1, approval
   
6. Add RoutingLine entries
   - Work center, sequence, hours
   - System calculates total labor cost


B. PRODUCTION ORDER PROCESS
----------------------------

1. Create ProductionOrder
   - Select product, quantity, dates
   - Auto-populated BOM and routing versions
   - System calculates estimated costs
   
2. Release to Shop Floor (status = RELEASED)
   - System triggers material reservations
   
3. Start Production (status = IN_PROGRESS)
   - Timing begins
   - Labor and material tracking
   
4. Quality Inspection
   - Create QualityInspection record
   - PASS: Move to completion
   - FAIL: Create rework order or scrap
   
5. Complete Production (status = COMPLETE)
   - Record actual materials used
   - Record actual labor hours
   - GL posting: Finished goods received
   - GL posting: WIP relieved
   
6. Cost Reconciliation
   - Compare actual vs. standard costs
   - Investigate variances


C. MAINTENANCE PROCESS
----------------------

1. Equipment preventive maintenance
   - Next_maintenance_date triggers
   - Create work order or task
   
2. Record maintenance
   - Update last_maintenance_date
   - Update next_maintenance_date
   
3. Emergency maintenance
   - Update status to MAINTENANCE or REPAIR
   - Affects production capacity


4. GL INTEGRATION
=================

AUTOMATIC GL POSTING (Post-Save Signals)

When ProductionOrder.status = 'COMPLETE':

  Journal Entry Created:
  ├─ Reference: MFG-{po_number}
  ├─ Date: Completion date
  ├─ Description: "Manufacturing Cost for {product_name}"
  │
  ├─ DEBIT:  Finished Goods Account
  │           Amount: actual_material_cost + actual_labor_cost
  │
  └─ CREDIT: Work-in-Progress Account
             Amount: actual_material_cost + actual_labor_cost

ACCOUNT MAPPING:

Product.inventory_account
  → Finished goods GL account
  → CURRENT ASSET type
  
WorkCenter.labor_expense_account
  → Labor cost clearing account
  → EXPENSE type
  
WorkCenter.machine_expense_account
  → Overhead cost clearing account
  → EXPENSE type
  
RawMaterial.inventory_account
  → Raw materials GL account
  → CURRENT ASSET type


COST FLOW TRACKING:

1. Raw Materials Purchased
   DR: Raw Materials Inventory
   CR: Accounts Payable

2. Materials Issued to Production (Future: Inventory Module)
   DR: Work in Process
   CR: Raw Materials Inventory

3. Labor Applied to Production (Future: Time Tracking)
   DR: Work in Process
   CR: Payroll Payable

4. Production Completed
   DR: Finished Goods Inventory
   CR: Work in Process (Actual cost)

5. Goods Sold
   DR: Cost of Goods Sold
   CR: Finished Goods Inventory (at actual cost)


5. MULTI-ENTITY SUPPORT
=======================

ENTITY FILTERING:

Every manufacturing record includes:
  - entity_id: Links to accounting.Entity
  
View Filtering:
  - get_user_entities(user) → List of entity IDs from UserRole
  - All querysets filtered: Model.objects.filter(entity_id__in=user_entities)
  
Form Initialization:
  - Single-entity users: Entity auto-selected
  - Multi-entity users: Entity selector shown


USER ROLES & PERMISSIONS:

Via accounting.role_models.UserRole:
  - Admin: All manufacturing operations
  - Manager: Create/edit/view orders
  - Operator: View and update status
  - Viewer: Read-only access


6. API ENDPOINTS
================

PRODUCT MANAGEMENT:
  GET    /manufacturing/products/
  POST   /manufacturing/products/new/
  GET    /manufacturing/products/<id>/
  POST   /manufacturing/products/<id>/edit/
  GET    /manufacturing/categories/
  POST   /manufacturing/categories/new/

BILL OF MATERIALS:
  GET    /manufacturing/bom/
  POST   /manufacturing/bom/new/
  GET    /manufacturing/bom/<id>/
  POST   /manufacturing/bom/<id>/edit/

RAW MATERIALS:
  GET    /manufacturing/materials/
  POST   /manufacturing/materials/new/
  GET    /manufacturing/materials/<id>/
  POST   /manufacturing/materials/<id>/edit/

PRODUCTION ORDERS:
  GET    /manufacturing/production-orders/
  POST   /manufacturing/production-orders/new/
  GET    /manufacturing/production-orders/<id>/
  POST   /manufacturing/production-orders/<id>/edit/

QUALITY CONTROL:
  GET    /manufacturing/inspections/
  POST   /manufacturing/inspections/new/
  GET    /manufacturing/inspections/<id>/

WORK CENTERS:
  GET    /manufacturing/work-centers/
  POST   /manufacturing/work-centers/new/

EQUIPMENT:
  GET    /manufacturing/equipment/
  POST   /manufacturing/equipment/new/

DASHBOARD:
  GET    /manufacturing/dashboard/


7. DASHBOARD METRICS
====================

Key Performance Indicators (KPIs):

- total_orders: All production orders
- open_orders: Status = RELEASED or IN_PROGRESS
- completed_orders: Status = COMPLETE
- failed_inspections: Quality issues (FAIL status)
- low_stock_materials: Below reorder point
- total_po_cost: Sum of actual manufacturing costs


USAGE QUERIES:

# Get manufacturing cost for period
PO_cost = ProductionOrder.objects.filter(
    completion_date__range=[start_date, end_date],
    status='COMPLETE'
).aggregate(
    total=Sum('actual_material_cost') + Sum('actual_labor_cost')
)['total']

# Find production delays
delayed = ProductionOrder.objects.filter(
    due_date__lt=Now(),
    status__in=['RELEASED', 'IN_PROGRESS']
)

# Quality defect rate
defect_rate = QualityInspection.objects.filter(
    status='FAIL'
).count() / QualityInspection.objects.all().count() * 100


8. USAGE EXAMPLES
=================

CREATING A NEW PRODUCT:

1. Create Category:
   ProductCategory.objects.create(
       entity_id=1,
       name='Electronics',
       code='ELEC'
   )

2. Create Product:
   Product.objects.create(
       entity_id=1,
       product_code='PROD-001',
       name='Widget Pro',
       standard_cost=Decimal('100.00'),
       selling_price=Decimal('150.00')
   )

3. Create BOM:
   bom = BillOfMaterials.objects.create(
       entity_id=1,
       product_id=1,
       version=1,
       effective_date=date.today()
   )
   
4. Add BOM Lines:
   BOMLine.objects.create(
       bom=bom,
       material_id=1,
       quantity_per_unit=Decimal('2.5'),
       scrap_percentage=Decimal('5'),
       unit_cost=Decimal('40.00')
   )

5. Create Routing:
   routing = Routing.objects.create(
       entity_id=1,
       product_id=1,
       version=1
   )

6. Add Routing Lines:
   RoutingLine.objects.create(
       routing=routing,
       work_center_id=1,
       sequence=1,
       estimated_hours=Decimal('2.0')
   )


CREATING A PRODUCTION ORDER:

order = ProductionOrder.objects.create(
    entity_id=1,
    po_number='PO-2024-001',
    product_id=1,
    quantity_ordered=Decimal('100'),
    start_date=date.today(),
    due_date=date.today() + timedelta(days=7),
    bom_id=1,
    routing_id=1,
    status='PLANNED',
    created_by=request.user
)

# Mark as released
order.status = 'RELEASED'
order.save()

# Complete production
order.status = 'COMPLETE'
order.quantity_completed = Decimal('100')
order.actual_material_cost = Decimal('250.00')
order.actual_labor_cost = Decimal('100.00')
order.completion_date = timezone.now().date()
order.save()
# → Triggers GL posting automatically


QUALITY INSPECTION:

inspection = QualityInspection.objects.create(
    entity_id=1,
    production_order=order,
    quantity_inspected=Decimal('100'),
    status='PASS',  # or FAIL, REWORK
    inspected_by=request.user
)


9. BEST PRACTICES
=================

PRODUCT SETUP:
  ✓ Always create BOM before creating production orders
  ✓ Use meaningful product codes (e.g., category prefix)
  ✓ Version BOMs when recipes change
  ✓ Require approval for BOM and routing changes
  
PRODUCTION PLANNING:
  ✓ Set reasonable lead times
  ✓ Batch orders to minimize setup
  ✓ Plan for scrap in BOM
  ✓ Consider equipment capacity
  
QUALITY CONTROL:
  ✓ Inspect per inspection_level setting
  ✓ Document defects for corrective action
  ✓ Track failure trends
  ✓ Implement preventive measures
  
COST CONTROL:
  ✓ Compare actual vs. standard costs
  ✓ Investigate variances > 10%
  ✓ Track scrap separately
  ✓ Review labor utilization
  
DATA QUALITY:
  ✓ Keep stock counts accurate
  ✓ Update equipment maintenance dates
  ✓ Audit for obsolete products/materials
  ✓ Archive old BOM/routing versions
  
PERFORMANCE:
  ✓ Use indexes on frequently searched fields
  ✓ Filter by entity early in queries
  ✓ Archive old production orders periodically
  ✓ Monitor database size


INTEGRATION WITH OTHER MODULES:
  - Accounting: GL posting, cost tracking
  - HR: Labor rate updates, attendance
  - Shareholder: Production KPIs for reporting
  - Future: Inventory, Procurement, Sales


END OF DOCUMENTATION
====================
"""

# This file documents the manufacturing module structure and usage.
# For implementation details, see models.py, forms.py, views.py
