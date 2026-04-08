# Purchase Order (PO) Accounting Flow

## 🎯 Design Principle: POs Do NOT Create GL Entries

A Purchase Order is a **commitment to buy**, not a financial transaction.

### ✅ Universal Procure-to-Pay Flow (Used by SAP, Oracle, NetSuite, Odoo, etc.)

```
1. Purchase Requisition
   ↓
   NO GL ENTRY

2. Purchase Order (PO)
   ↓
   NO GL ENTRY
   ✓ Tracks commitment
   ✓ Stores supplier, items, quantities, dates
   ✓ May track budget commitment (non-GL)

3. Goods Receipt (GRN / Goods Issue)
   ↓
   GL Entry Created:
   DR: Inventory (Raw Materials)        [Asset Account]
   CR: GR/IR Clearing Account           [Liability Account]
   
   ✓ Why? You now own the goods
   ✓ Why clearing? Supplier hasn't invoiced yet

4. Supplier Invoice (AP Invoice)
   ↓
   GL Entry Created:
   DR: GR/IR Clearing Account           [Liability Account]
   CR: Accounts Payable (AP)            [Liability Account]
   
   ✓ Invoice matched to PO and GRN
   ✓ Official liability recorded with supplier

5. Payment (Check/Wire/ACH)
   ↓
   GL Entry Created:
   DR: Accounts Payable (AP)            [Liability Account]
   CR: Bank / Cash Account              [Asset Account]
   
   ✓ Liability is cleared
   ✓ Cash reduced
```

---

## 🔑 Key Accounts in Raw Material Procurement

| Account | Type | Purpose | When Created |
|---------|------|---------|--------------|
| **Raw Material Inventory** | Asset | Stores cost of goods received | Goods Receipt |
| **GR/IR Clearing Account** | Clearing | Temporary placeholder | Goods Receipt |
| **Accounts Payable (AP)** | Liability | Official supplier debt | Invoice Receipt |
| **Bank / Cash** | Asset | Payment method | Payment |

---

## 🛠️ Implementation Status in TradifyERP

### ✅ Phase 1: Purchase Order (Current)
- [x] Create PO with supplier and items
- [x] Store PO number, dates, payment terms
- [x] No GL entries created ← **CORRECT**
- [ ] PO approval workflow
- [ ] Budget reservation (non-GL tracking)

### 🟡 Phase 2: Goods Receipt (GRN) - TO DO
- [ ] Create GRN linked to PO
- [ ] Select items and quantities received
- **Create GL Entry:**
  - DR: Raw Material Inventory
  - CR: GR/IR Clearing Account

### 🟡 Phase 3: Invoice Receipt (AP Invoice) - TO DO
- [ ] Create AP Invoice linked to PO and GRN
- [ ] Match invoice to PO and GRN (3-way matching)
- **Create GL Entry:**
  - DR: GR/IR Clearing Account
  - CR: Accounts Payable

### 🟡 Phase 4: Payment - TO DO
- [ ] Create Payment linked to AP Invoice
- [ ] Select payment method (check, wire, etc.)
- **Create GL Entry:**
  - DR: Accounts Payable
  - CR: Bank Account

---

## 📋 Current PO Form (Correct Implementation)

**Fields:**
- Supplier (required)
- Entity (required)
- PO Number
- Expected Delivery Date
- Payment Terms
- Total Amount

**NO accounting-related fields** ← This is correct! Accounting happens later.

---

## 🚀 Next Steps for Complete Procurement

1. **Goods Receipt (GRN) Module**
   - Accept delivery of goods
   - Match to PO
   - Trigger GL: Inventory DR / GR/IR Clearing CR

2. **Invoice Receipt (AP) Module**
   - Receive supplier invoice
   - Three-way matching (PO ↔ GRN ↔ Invoice)
   - Trigger GL: GR/IR Clearing DR / AP CR

3. **Payment Module**
   - Record payment to supplier
   - Trigger GL: AP DR / Bank CR
   - Update bank reconciliation

4. **Reporting**
   - Pending goods (PO without GRN)
   - Pending invoices (GRN without Invoice)
   - Pending payments (Invoice without Payment)

---

## 📚 References

- **SAP**: Material Receipt (MIGO) → Invoice (MIRO) → Payment (FBZ8)
- **Oracle**: Receipt → AP Invoice → Payment
- **NetSuite**: Purchase Order → Item Receipt → Bill → Check
- **Odoo**: PO → Receipt → Bill (Invoice) → Payment

All follow this same pattern: **PO has NO GL impact**.

---

## ⚠️ Common Mistake

**WRONG:**
```
PO Creation
  ↓
Deduct from some GL account
  ↓
GL Entry created
```

**CORRECT:**
```
PO Creation
  ↓
No GL entry
  ↓
Goods Receipt
  ↓
GL Entry created
```
