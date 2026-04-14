# Raw Materials Management System - Implementation Plan
## For TradifyERP Bio-Plastics Manufacturing

**Date**: April 7, 2026  
**Status**: Planning Phase  
**Priority**: HIGH - Core to Manufacturing Operations

---

## 📋 OVERVIEW

Your bio-plastics manufacturing requires a dedicated **Raw Materials Management Module** to handle:
- Raw material inventory tracking
- Automated purchase order generation
- Supplier management
- Stock level monitoring
- Low stock alerts & reordering
- Cost tracking and variance analysis
- Material consumption tracking (by production orders)

---

## 🎯 REQUIREMENTS ANALYSIS

### Raw Materials Identified

| Product Code | Raw Material Name | Description | Unit | Category |
|--------------|-------------------|-------------|------|----------|
| RM-PBAT-001 | PBAT Granules | Flexible biodegradable polymer for film blowing | KG | Polymer Base |
| RM-PLA-002 | PLA Granules | Plant-based biodegradable plastic from starch | KG | Polymer Base |
| RM-CS-003 | Corn Starch | Natural starch for biodegradable polymer blends | KG | Fiber/Filler |
| RM-TPS-004 | Thermoplastic Starch | Modified starch in compostable plastics | KG | Fiber/Filler |
| RM-CACO3-005 | Calcium Carbonate | Filler material to improve strength & reduce cost | KG | Filler/Additive |
| RM-MB-006 | Color Masterbatch | Color additive for biodegradable plastics | KG | Additive |
| RM-TIO2-007 | Titanium Dioxide | White pigment for plastic film color | KG | Additive |
| RM-PLAST-008 | Glycerol Plasticizer | Plasticizer to improve flexibility | KG | Additive |
| RM-STAB-009 | Biodegradable Stabilizer | Improves polymer processing stability | KG | Additive |
| RM-MESH-010 | Biodegradable Mesh Material | Used for breathable produce bags | KG | Specialty Material |
| RM-NWF-011 | Non-woven PLA Fabric | Used for aprons and salon capes | KG | Specialty Material |
| RM-PLAFILM-012 | PLA Film Roll | Film material for ponchos and covers | KG | Specialty Material |
| RM-PACK-013 | Packaging Poly Roll | Roll for packing finished products | KG | Packaging |
| RM-LABEL-014 | Product Labels | Printed labels for product packaging | PCS | Packaging |
| RM-CARTON-015 | Carton Boxes | Boxes for shipping products | PCS | Packaging |

**Total Raw Materials**: 15  
**Categories**: 6 (Polymer Base, Fiber/Filler, Additive, Specialty Material, Packaging, Filler/Additive)

---

## 🏗️ SYSTEM DESIGN

### Module Architecture

```
┌─────────────────────────────────────────────────────────┐
│           RAW MATERIALS MANAGEMENT MODULE               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  Raw         │  │  Stock        │  │  Ordering &  │ │
│  │  Materials   │→ │  Management   │→ │  Procurement │ │
│  │  Master      │  │  & Tracking   │  │  System      │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│       ↓                  ↓                   ↓          │
│  ┌─────────────────────────────────────────────────┐   │
│  │     SUPPLIER & COST MANAGEMENT                  │   │
│  │  (Supplier List, Pricing, Payment Terms)       │   │
│  └─────────────────────────────────────────────────┘   │
│       ↓                                                 │
│  ┌─────────────────────────────────────────────────┐   │
│  │     ALERTS & NOTIFICATIONS                      │   │
│  │  (Low Stock, Auto-PO, Delivery Reminders)      │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Integration Points

```
Raw Materials Module
    ↓
    ├→ PROCUREMENT (Generate PO automatically)
    ├→ ACCOUNTING (Track material costs)
    ├→ INVENTORY (Update stock levels)
    ├→ AP (Manage supplier bills)
    ├→ MANUFACTURING (Track consumption in BOM)
    └→ REPORTS (Material cost analysis)
```

---

## 📊 DATABASE DESIGN

### 1. Raw Material Master (Core Data)

```sql
CREATE TABLE raw_materials_raw_material (
    id BIGINT PRIMARY KEY,
    product_code VARCHAR(50) UNIQUE,          -- RM-PBAT-001
    name VARCHAR(255),                        -- PBAT Granules
    description TEXT,
    category VARCHAR(100),                    -- Polymer, Filler, Additive, etc.
    unit_of_measure VARCHAR(20),              -- KG, PCS
    
    -- Specifications
    hsn_code VARCHAR(20),                     -- For GST/Tax
    density DECIMAL(10, 2),                   -- For material estimation
    is_recyclable BOOLEAN,
    biodegradability_period VARCHAR(100),     -- For eco marketing
    
    -- Cost Tracking
    current_unit_price DECIMAL(12, 2),
    last_price_update_date DATE,
    average_price_last_year DECIMAL(12, 2),
    supplier_id REFERENCES suppliers,
    
    -- Status
    is_active BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### 2. Stock Management

```sql
CREATE TABLE raw_materials_stock (
    id BIGINT PRIMARY KEY,
    raw_material_id REFERENCES raw_materials_raw_material,
    
    -- Stock Levels
    quantity_on_hand DECIMAL(12, 2),          -- Current stock
    quantity_reserved DECIMAL(12, 2),         -- Reserved for production orders
    quantity_available DECIMAL(12, 2),        -- Available = On Hand - Reserved
    quantity_damaged DECIMAL(12, 2),          -- Damaged/unusable stock
    
    -- Thresholds & Triggers
    minimum_stock_level DECIMAL(12, 2),       -- Trigger reorder
    maximum_stock_level DECIMAL(12, 2),       -- Don't order beyond this
    reorder_quantity DECIMAL(12, 2),          -- Order quantity
    lead_time_days INT,                       -- Days to receive after ordering
    
    -- Valuation
    valuation_method VARCHAR(20),             -- FIFO, LIFO, Weighted Average
    standard_cost DECIMAL(12, 2),
    actual_cost DECIMAL(12, 2),
    warehouse_location VARCHAR(100),          -- Bin number/location
    
    last_stock_check_date DATE,
    updated_at TIMESTAMP
);
```

### 3. Stock Movements (For Audit Trail)

```sql
CREATE TABLE raw_materials_stock_movement (
    id BIGINT PRIMARY KEY,
    raw_material_id REFERENCES raw_materials_raw_material,
    
    movement_type VARCHAR(50),                -- IN (Purchase), OUT (Production), 
                                             -- ADJUSTMENT, DAMAGE
    quantity DECIMAL(12, 2),
    unit_price DECIMAL(12, 2),
    total_value DECIMAL(15, 2),
    
    -- Reference to source
    purchase_order_id REFERENCES Procurement,
    production_order_id REFERENCES Manufacturing,
    reference_number VARCHAR(100),
    
    notes TEXT,
    created_at TIMESTAMP,
    created_by REFERENCES User
);
```

### 4. Supplier Management

```sql
CREATE TABLE raw_materials_supplier (
    id BIGINT PRIMARY KEY,
    supplier_name VARCHAR(255),
    supplier_code VARCHAR(50) UNIQUE,
    contact_person VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    
    -- Payment Terms
    payment_terms VARCHAR(100),               -- NET 30, 2/10 NET 30
    credit_limit DECIMAL(15, 2),
    currency VARCHAR(10),
    
    -- Ratings
    quality_rating DECIMAL(3, 1),             -- 1-5 stars
    delivery_rating DECIMAL(3, 1),
    pricing_competitive BOOLEAN,
    
    -- Certification
    iso_certified BOOLEAN,
    quality_certifications TEXT,              -- ISO, BIS, etc.
    
    is_active BOOLEAN,
    created_at TIMESTAMP
);
```

### 5. Purchase Orders (Specific to Raw Materials)

```sql
CREATE TABLE raw_materials_purchase_order (
    id BIGINT PRIMARY KEY,
    po_number VARCHAR(50) UNIQUE,
    po_date DATE,
    supplier_id REFERENCES raw_materials_supplier,
    
    -- Items
    raw_material_id REFERENCES raw_materials_raw_material,
    quantity_ordered DECIMAL(12, 2),
    unit_price DECIMAL(12, 2),
    line_total DECIMAL(15, 2),
    
    -- Delivery
    expected_delivery_date DATE,
    actual_delivery_date DATE,
    delivery_warehouse_location VARCHAR(100),
    
    -- Approval & Status
    po_status VARCHAR(50),                    -- Draft, Approved, Ordered, Received, 
                                             -- Cancelled
    approval_date DATE,
    approved_by REFERENCES User,
    
    -- Notes
    notes TEXT,
    created_at TIMESTAMP,
    created_by REFERENCES User
);
```

### 6. Auto-Reorder System

```sql
CREATE TABLE raw_materials_auto_reorder_setting (
    id BIGINT PRIMARY KEY,
    raw_material_id REFERENCES raw_materials_raw_material,
    
    -- Trigger Conditions
    is_auto_reorder_enabled BOOLEAN,
    min_stock_to_trigger_order DECIMAL(12, 2),
    auto_reorder_quantity DECIMAL(12, 2),
    
    -- Preferred Supplier
    preferred_supplier_id REFERENCES raw_materials_supplier,
    
    -- Notification
    notify_before_days INT,                   -- Notify X days before stock runs out
    
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### 7. Low Stock Alerts

```sql
CREATE TABLE raw_materials_stock_alert (
    id BIGINT PRIMARY KEY,
    raw_material_id REFERENCES raw_materials_raw_material,
    alert_type VARCHAR(50),                  -- LOW_STOCK, OUT_OF_STOCK, 
                                            -- EXPIRY_SOON, QUALITY_ISSUE
    
    severity VARCHAR(20),                    -- LOW, MEDIUM, HIGH, CRITICAL
    message TEXT,
    
    -- Alert Status
    is_active BOOLEAN,
    is_acknowledged BOOLEAN,
    acknowledged_by REFERENCES User,
    acknowledged_at TIMESTAMP,
    
    action_taken TEXT,                       -- What was done to resolve
    resolved_at TIMESTAMP,
    
    created_at TIMESTAMP
);
```

---

## 🎬 KEY FEATURES

### 1. Raw Materials Master
- [x] Create/Edit/Delete raw materials
- [x] Assign to suppliers
- [x] Track material specifications
- [x] Sustainability/Biodegradability details
- [x] Material categorization

### 2. Stock Management
- [x] Real-time stock levels
- [x] Available vs. Reserved tracking
- [x] Multiple warehouse locations
- [x] Stock valuation methods (FIFO/LIFO/Weighted Avg)
- [x] Stock movement audit trail
- [x] Damaged stock tracking

### 3. Ordering System
- [x] Generate POs from low stock levels
- [x] Multiple supplier selection
- [x] Bulk order discounts
- [x] Lead time tracking
- [x] Delivery tracking
- [x] Goods receipt confirmation

### 4. Automated Alerts
- [x] Low stock warnings
- [x] Out of stock alerts
- [x] Auto-reorder triggers
- [x] Delivery reminders
- [x] Quality/Expiry alerts
- [x] Budget variance alerts

### 5. Supplier Management
- [x] Supplier master data
- [x] Quality ratings
- [x] Delivery performance tracking
- [x] Certification tracking
- [x] Payment terms management
- [x] Price negotiation history

### 6. Reporting & Analytics
- [x] Material cost variance analysis
- [x] Consumption trends by product
- [x] Supplier performance reports
- [x] Stock aging reports
- [x] Budget vs. Actual analysis
- [x] Sustainability metrics

### 7. Integration
- [x] Link to Manufacturing (BOM consumption)
- [x] Link to Procurement (auto PO)
- [x] Link to Accounting (material costs)
- [x] Link to Inventory (stock levels)
- [x] Link to AP (supplier bills)

---

## 🔄 WORKFLOW

### Material Ordering Workflow

```
1. System monitors stock levels (Daily)
   ↓
2. If quantity_on_hand < minimum_stock_level
   ↓
3. Generate Alert "Low Stock Warning"
   ↓
4. If auto_reorder_enabled = TRUE
   ↓
5. Create Draft Purchase Order
   ↓
6. Send for approval to Manager
   ↓
7. If approved → Auto-send to supplier
   ↓
8. Create GRN (Goods Receipt Note) on receipt
   ↓
9. Update Stock Levels
   ↓
10. Create AP Invoice
```

### Production Consumption Workflow

```
Production Order Created
   ↓
BOM specified with Raw Materials
   ↓
System calculates material needed
   ↓
Check Available Stock
   ↓
If sufficient: Reserve stock
If insufficient: Generate Purchase Requisition
   ↓
Update Reserved Quantity
   ↓
Manufacturing starts
   ↓
On production completion:
   Deduct actual consumption from stock
   ↓
Update Stock Levels
```

---

## 📱 USER INTERFACE REQUIREMENTS

### Dashboard Widgets
- [ ] Total Raw Materials Inventory Value (KPIs)
- [ ] Low Stock Items (Table)
- [ ] Stock Turnover Ratio (Charts)
- [ ] Pending Purchase Orders (List)
- [ ] Supplier Performance (Ratings)
- [ ] Cost Trends (Graph)

### Forms & Pages
- [ ] Raw Material Master (CRUD)
- [ ] Stock Level Management
- [ ] Purchase Order Generation
- [ ] Supplier Management
- [ ] Stock Receipt & GRN
- [ ] Reorder Settings
- [ ] Alert Configuration

### Reports
- [ ] Stock Valuation Report
- [ ] Material Consumption Report
- [ ] Supplier Price Comparison
- [ ] Stock Aging Report
- [ ] Procurement Variance
- [ ] Environmental Impact (Biodegradability)

---

## 🛠️ IMPLEMENTATION APPROACH

### Phase 1: Foundation (Week 1-2)
1. Create Raw Materials module
2. Build database models
3. Create Raw Material Master forms
4. Implement stock management

### Phase 2: Ordering (Week 3-4)
1. Build Purchase Order system
2. Integrate with Procurement
3. Create GRN (Goods Receipt Notes)
4. Supplier management

### Phase 3: Automation (Week 5-6)
1. Implement auto-reorder logic
2. Create alert system
3. Stock threshold configuration
4. Notification system

### Phase 4: Integration & Reports (Week 7-8)
1. Connect to Manufacturing BOM
2. Link to Accounting (material costs)
3. Create dashboards
4. Build reports

---

## 💾 MIGRATION DATA

### Import from Your Spreadsheet
- 15 Raw Materials
- Unit of Measure (KG, PCS)
- Descriptions & specifications
- Supplier information (to be added)
- Current pricing (to be added)

---

## 🔐 SECURITY & PERMISSIONS

### Role-Based Access
- **Warehouse Manager**: View stock, create receipts
- **Procurement Manager**: Create POs, approve orders
- **Production Manager**: View available materials, reserve for BOM
- **Accounting**: View material costs, track expenses
- **Admin**: Configure settings, manage suppliers, create alerts

---

## ✅ SUCCESS CRITERIA

- [x] All 15 raw materials created in system
- [x] Stock levels tracked automatically
- [x] Purchase orders generated when stock is low
- [x] Alerts triggered for critical stock levels
- [x] Suppliers tracked with performance ratings
- [x] Material costs integrated with accounting
- [x] Production orders show material availability
- [x] Dashboard shows real-time inventory status

---

## 📊 RECOMMENDED ORDER FOR IMPLEMENTATION

1. **Create Raw Materials Master** (Import 15 items)
2. **Stock Management System** (Track inventory)
3. **Supplier Management** (Link suppliers)
4. **Purchase Order System** (Auto-generate)
5. **Alert/Notification System** (Warnings)
6. **Manufacturing Integration** (BOM consumption)
7. **Reports & Dashboard** (Analytics)

---

## 🚀 NEXT STEPS

1. Review this design document
2. Get approval to proceed
3. Confirm supplier information
4. Set up stock thresholds
5. Start Phase 1 implementation

**Estimated Total Time**: 8 weeks (4 phases)  
**Complexity**: High (Many integrations)  
**Business Impact**: CRITICAL (Core to manufacturing)

---

**Document Created**: April 7, 2026  
**Status**: Ready for Implementation  
**Restore Point**: Available (2026-04-07_pre-enhancement)
