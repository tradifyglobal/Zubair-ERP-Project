# Manufacturing Module - Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Manufacturing Module                        │
│                    (5000+ lines of code)                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
         ┌──────▼───┐   ┌────▼─────┐   ┌──▼────────┐
         │ Models   │   │ Views     │   │ Forms     │
         │ (1400L)  │   │ (700L)    │   │ (300L)    │
         └──────────┘   └───────────┘   └───────────┘
                │             │             │
                └─────────────┼─────────────┘
                              │
                     ┌────────▼────────┐
                     │  Signals (GL)   │
                     │  Integration    │
                     └────────┬────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
    ┌────▼────┐          ┌────▼────┐          ┌──▼────┐
    │Database │          │ GL Acct │          │ URL   │
    │(13 Tbl) │          │ Posting │          │Route  │
    └─────────┘          └─────────┘          └───────┘
```

## Data Model Hierarchy

```
PRODUCT STRUCTURE
═════════════════

Entity (from Accounting)
  │
  ├─ ProductCategory
  │   └─ Product (FG)
  │       ├─ BillOfMaterials (v1, v2...)
  │       │   └─ BOMLine
  │       │       └─ RawMaterial (inventory)
  │       └─ Routing (v1, v2...)
  │           └─ RoutingLine
  │               └─ WorkCenter
  │
  └─ ProductionOrder
      ├─ (references Product, BOM, Routing)
      ├─ QualityInspection
      └─ JournalEntry (GL auto-post)
```

## Request Processing Flow

```
User Request
    │
    ▼
URL Route (/manufacturing/...)
    │
    ▼
View (with @csrf_protect)
    │
    ├─ LoginRequiredMixin Check ✓
    │
    ├─ get_user_entities(request.user)
    │
    ├─ Filter queryset by entity
    │
    └─ If POST:
        │
        ├─ Validate CSRF token ✓
        │
        ├─ Bind form with data
        │
        ├─ Run form validation
        │
        ├─ If valid:
        │   │
        │   ├─ Set entity
        │   ├─ Set created_by
        │   ├─ Save to database
        │   │
        │   ├─ Trigger signals
        │   │   └─ GL posting logic
        │   │
        │   └─ Redirect
        │
        └─ If invalid:
            └─ Re-render with errors
```

## Multi-Entity Filtering Architecture

```
┌─────────────────────────────────────┐
│        User Logs In                 │
│     (request.user = 'zubair')       │
└──────────────┬──────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│ Query UserRole                       │
│ .filter(user=zubair, is_active=True) │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│ Extract entity_id list              │
│ user_entities = [1, 2, 3, ...]      │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│ Filter all querysets                 │
│ .filter(entity_id__in=user_entities) │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│ User sees only accessible data       │
│ (Multi-entity, multi-tenant)        │
└──────────────────────────────────────┘
```

## GL Integration (Signals) Flow

```
ProductionOrder Created
    │
    ├─ Status: DRAFT
    └─ No GL impact

ProductionOrder Status Change
    │
    ├─ DRAFT → PLANNED
    ├─ PLANNED → RELEASED
    └─ RELEASED → IN_PROGRESS
       (No GL impact yet)

ProductionOrder Completed
    │
    ├─ Status: COMPLETE ✓ TRIGGER
    │
    ├─ Post-save signal fires
    │
    ├─ Check if GL entry exists
    │   └─ Skip if already posted
    │
    ├─ Retrieve GL accounts:
    │   ├─ Finished Goods Account
    │   └─ WIP Account
    │
    ├─ Create JournalEntry:
    │   │
    │   ├─ entity = PO.entity
    │   ├─ date = timezone.now().date()
    │   ├─ reference = f"MFG-{po_number}"
    │   ├─ status = 'POSTED'
    │   │
    │   ├─ JournalEntryLine 1:
    │   │   ├─ account = Finished Goods
    │   │   ├─ debit = actual_cost
    │   │   └─ credit = 0
    │   │
    │   └─ JournalEntryLine 2:
    │       ├─ account = WIP
    │       ├─ debit = 0
    │       └─ credit = actual_cost
    │
    └─ GL Posted ✓
```

## Form Processing Pipeline

```
GET Request
    │
    ├─ View: get_context_data()
    │   │
    │   ├─ get_token(request) ✓
    │   │
    │   └─ context['csrf_token'] = token
    │
    └─ Template renders with {% csrf_token %}

POST Request with CSRF Token
    │
    ├─ Middleware validates token ✓
    │
    ├─ View: form_valid()
    │   │
    │   ├─ form.save(commit=False)
    │   │   (Don't save yet)
    │   │
    │   ├─ Set required fields:
    │   │   ├─ instance.entity_id
    │   │   ├─ instance.created_by
    │   │   └─ instance.created_at
    │   │
    │   ├─ instance.save()
    │   │   (Now save with defaults)
    │   │
    │   ├─ Signals fire ✓
    │   │
    │   └─ Redirect to list view
    │
    └─ Success ✓
```

## Database Schema Structure

```
TABLES CREATED (13)
═══════════════════

ProductCategory
├─ id (PK)
├─ entity_id (FK) ──────┐
├─ name                 │
├─ code                 │
├─ revenue_account_id   │
├─ cogs_account_id      │
├─ is_active            │
├─ created_at           │
└─ updated_at           │
                        │
Product                 │
├─ id (PK)              │
├─ entity_id (FK) ──────┼─┐
├─ product_code         │ │
├─ name                 │ │
├─ category_id (FK) ────┘ │
├─ is_manufactured      │
├─ standard_cost        │
├─ selling_price        │
├─ inventory_account_id │
├─ created_by_id (FK)   │
├─ created_at           │
└─ updated_at           │
                        │
RawMaterial             │
├─ id (PK)              │
├─ entity_id (FK) ──────┼─┐
├─ material_code        │ │
├─ name                 │ │
├─ current_stock        │ │
├─ reorder_point        │ │
├─ standard_unit_cost   │ │
├─ inventory_account_id │ │
└─ ...                  │ │
                        │ │
BillOfMaterials         │ │
├─ id (PK)              │ │
├─ entity_id (FK) ──────┼─┼─┐
├─ product_id (FK) ─────┘ │ │
├─ version              │ │
├─ effective_date       │ │
├─ created_by_id        │ │
└─ ...                  │ │
                        │ │
BOMLine                 │ │
├─ id (PK)              │ │
├─ bom_id (FK) ─────────┘ │
├─ material_id (FK) ────┐  │
├─ quantity_per_unit    │  │
├─ scrap_percentage     │  │
└─ ...                  │  │
                        │  │
WorkCenter              │  │
├─ id (PK)              │  │
├─ entity_id (FK) ──────┼──┼─┐
├─ code                 │  │ │
├─ name                 │  │ │
├─ labor_cost_per_hour  │  │ │
├─ machine_cost_per_hour│  │ │
└─ ...                  │  │ │
                        │  │ │
Routing                 │  │ │
├─ id (PK)              │  │ │
├─ entity_id (FK) ──────┼──┼─┼─┐
├─ product_id (FK) ─────┘  │ │ │
├─ version              │  │ │ │
├─ created_by_id        │  │ │ │
└─ ...                  │  │ │ │
                        │  │ │ │
RoutingLine             │  │ │ │
├─ id (PK)              │  │ │ │
├─ routing_id (FK) ─────┘  │ │ │
├─ work_center_id (FK) ────┘ │ │
├─ sequence                │ │
└─ ...                  │  │ │
                        │  │ │
ProductionOrder         │  │ │
├─ id (PK)              │  │ │
├─ entity_id (FK) ──────┼──┼─┼─┐
├─ po_number            │  │ │ │
├─ product_id (FK) ─────┘  │ │ │
├─ bom_id (FK) ───────────┘ │ │
├─ routing_id (FK) ────────┘ │
├─ status               │  │
├─ quantity_ordered     │  │
├─ actual_material_cost │  │
├─ actual_labor_cost    │  │
├─ completion_date      │  │
├─ created_by_id        │  │
└─ ...                  │  │
                        │  │
QualityInspection       │  │
├─ id (PK)              │  │
├─ entity_id (FK) ──────┼──┼──┐
├─ production_order_id  │  │  │
├─ status               │  │  │
├─ defect_count         │  │  │
├─ inspected_by_id      │  │  │
└─ ...                  │  │  │
                        │  │  │
Equipment               │  │  │
├─ id (PK)              │  │  │
├─ entity_id (FK) ──────┼──┼──┘
├─ equipment_code       │  │
├─ status               │  │
├─ acquisition_cost     │  │
└─ ...                  │  │
                        │  │
                        └──┴─ Entity (from Accounting)
```

## View Layer Architecture

```
BASE CLASSES
════════════

LoginRequiredMixin
    └─ All manufacturing views use this

@method_decorator(csrf_protect, name='dispatch')
    └─ All views decorated with this

View Hierarchy:
    ListView
    ├─ get_queryset()
    │   ├─ get_filtered_queryset(Model, user)
    │   ├─ Filter by search
    │   └─ Filter by status/category/etc
    │
    ├─ get_context_data()
    │   └─ get_token(request)
    │
    └─ Template: list.html

CreateView
    ├─ get_form_kwargs()
    │   └─ Auto-populate entity for single-entity users
    │
    ├─ form_valid()
    │   ├─ form.save(commit=False)
    │   ├─ instance.entity_id = user_entities[0]
    │   ├─ instance.created_by = request.user
    │   ├─ instance.save()
    │   └─ Signals fire here
    │
    ├─ get_context_data()
    │   └─ get_token(request)
    │
    └─ Template: form.html

UpdateView / DeleteView
    ├─ get_queryset()
    │   └─ Filter by user's entities only
    │
    └─ Template: form.html / confirm_delete.html
```

## Performance Optimization Strategy

```
DATABASE LEVEL
══════════════
Indexes:
  ├─ ProductionOrder(po_number)
  ├─ ProductionOrder(status, due_date)
  ├─ ProductionOrder(entity_id, status)
  ├─ Product(product_code)
  ├─ Product(entity_id, is_active)
  ├─ RawMaterial(material_code)
  └─ RawMaterial(entity_id, is_active)

Queries:
  ├─ Paginate lists (25 items)
  ├─ Filter by entity early
  ├─ Use .values() for reports
  └─ Select_related/prefetch_related (in templates)

TEMPLATE LEVEL
═════════════
Caching:
  ├─ Product categories (rarely change)
  ├─ Work center rates (monthly)
  └─ GL account mappings

VIEWS
═════
Filtering:
  ├─ Entity at query level
  ├─ Status pre-filtered
  └─ Search indexed fields
```

## Security Architecture

```
AUTHENTICATION
═══════════════
1. User logs in
   └─ Django session created

2. Request arrives
   ├─ LoginRequiredMixin checks session
   └─ Redirects to login if not authenticated

AUTHORIZATION
══════════════
1. UserRole model filters
   ├─ User → Entity → Role mapping
   └─ Entity_id list extracted

2. Querysets filtered
   ├─ .filter(entity_id__in=user_entities)
   └─ User can only see/edit their entity

CSRF PROTECTION
═════════════════
1. View initialization
   ├─ @csrf_protect decorator
   └─ get_token(request)

2. Form rendering
   ├─ {% csrf_token %} tag
   └─ Token embedded in HTML

3. Form submission
   ├─ Middleware validates token
   ├─ Compares with session
   └─ Rejects if mismatch
```

## Cost Calculation Flow

```
STANDARD COSTING
════════════════

BOM Created:
  ├─ For each BOMLine
  │   ├─ quantity_per_unit = 2.5
  │   ├─ unit_cost = $40.00
  │   ├─ scrap_percentage = 5%
  │   │
  │   └─ total_cost = 2.5 × 40 × (1 + 0.05)
  │       = 2.5 × 40 × 1.05
  │       = $105.00
  │
  ├─ Sum all lines
  └─ total_bom_cost = $105 + $200 + $50 = $355 per unit

ProductionOrder Created:
  ├─ quantity_ordered = 100
  │
  ├─ estimated_material_cost = $355 × 100 = $35,500
  │
  └─ estimated_labor_cost = (hours × hourly_rate) × 100

ProductionOrder Completed:
  ├─ Actual material cost = $36,200 (variances recorded)
  ├─ Actual labor cost = $10,300
  │
  └─ GL Entry Posted:
      DR Finished Goods     $46,500
      CR Work in Process    $46,500
```

## Status Workflow State Machine

```
ProductionOrder States:
═════════════════════

    ┌─────────┐
    │ DRAFT   │
    └────┬────┘
         │ (Approve)
         ▼
    ┌─────────┐
    │ PLANNED │
    └────┬────┘
         │ (Release)
         ▼
    ┌────────────┐
    │ RELEASED   │
    └────┬───────┘
         │ (Start)
         ▼
    ┌──────────────┐
    │ IN_PROGRESS  │
    └────┬─────────┘
         │ (Complete)
         ▼
    ┌──────────┐
    │ COMPLETE │  ◄── GL Posting Triggered
    └──────────┘

    Alternative:
    DRAFT → CANCELLED (any time)
```

## Testing Matrix

```
UNIT TESTS
══════════
Models:
  ├─ All foreign keys valid
  ├─ All required fields present
  ├─ All calculations correct
  └─ Constraints enforced

INTEGRATION TESTS
═════════════════
Views:
  ├─ CSRF protection working
  ├─ Entity filtering working
  ├─ Form validation working
  └─ Redirects correct

GL Integration:
  ├─ JournalEntry created
  ├─ Correct GL accounts used
  ├─ Proper debit/credit
  └─ Reference populated

FUNCTIONAL TESTS
════════════════
Workflows:
  ├─ Product creation
  ├─ BOM creation
  ├─ PO creation
  ├─ PO completion
  └─ GL verification
```

---

**Complete Manufacturing Module Architecture**
