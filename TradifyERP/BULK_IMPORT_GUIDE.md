# Bulk Import Capital Contributions from Shareholder List

## Quick Start (3 Steps)

### Step 1: Export Your Shareholders
1. Go to **Shareholders** page
2. Click **Export → Export as CSV**
3. Save as `shareholders.csv`

### Step 2: Generate Contribution Template
Open PowerShell in your project directory and run:

```powershell
# For CSV template
python generate_contribution_import.py --input shareholders.csv --output contributions.csv

# For Excel template (recommended)
python generate_contribution_import.py --input shareholders.csv --output contributions.xlsx --format excel
```

### Step 3: Fill & Import
1. Open `contributions.xlsx` in Excel
2. Fill in **Amount** column (this is required!)
3. Adjust other columns as needed:
   - **Contribution Date** - When was the contribution made? (format: YYYY-MM-DD)
   - **Currency** - INR, USD, GBP, etc.
   - **Payment Mode** - BANK_TRANSFER, CHEQUE, CASH, etc.
   - **Status** - PENDING or COMPLETED
4. Save the file
5. Go to **Capital Contributions** page
6. Click **Import** button
7. Select your filled `contributions.xlsx` file
8. Click **Import**

---

## Step-by-Step Visual Guide

### Example: Using the Generated Template

**Your shareholder data:**
```
ID   First Name  Last Name
48   Mohammad    Sanaullah
49   Syed        Arif
50   Mohammad    Rafi
51   Syed        Safi
```

**Generated template (contributions.xlsx):**
| Stakeholder Name      | First Name | Last Name | Contribution Date | Amount | Currency | Payment Mode    | Status    |
|----------------------|-----------|-----------|------------------|--------|----------|-----------------|-----------|
| Mohammad Sanaullah   | Mohammad  | Sanaullah | 2025-12-01        | **???** | INR      | BANK_TRANSFER   | COMPLETED |
| Syed Arif            | Syed      | Arif      | 2025-12-01        | **???** | INR      | BANK_TRANSFER   | COMPLETED |
| Mohammad Rafi        | Mohammad  | Rafi      | 2025-12-01        | **???** | INR      | BANK_TRANSFER   | COMPLETED |
| Syed Safi            | Syed      | Safi      | 2025-12-01        | **???** | INR      | BANK_TRANSFER   | COMPLETED |

**After filling in amounts:**
| Stakeholder Name      | Contribution Date | Amount  | Currency | Payment Mode    | Status    |
|----------------------|------------------|---------|----------|-----------------|-----------|
| Mohammad Sanaullah   | 2025-01-15       | 100000  | INR      | BANK_TRANSFER   | COMPLETED |
| Syed Arif            | 2025-01-16       | 50000   | INR      | CHEQUE          | COMPLETED |
| Mohammad Rafi        | 2025-01-17       | 75000   | INR      | BANK_TRANSFER   | PENDING   |
| Syed Safi            | 2025-01-18       | 60000   | INR      | BANK_TRANSFER   | COMPLETED |

Then import this file - the system will:
- ✅ Match "Mohammad Sanaullah" to shareholder ID 48
- ✅ Create contribution of 100,000 INR on 2025-01-15
- ✅ Mark as COMPLETED
- ✅ Repeat for all rows
- ✅ Update total invested for each shareholder

---

## Column Reference

### Required Columns:
| Column | Format | Example | Notes |
|--------|--------|---------|-------|
| **Stakeholder Name** | "First Last" | "Mohammad Sanaullah" | Used to match shareholder |
| **Amount** | Number | 100000 | Contribution amount |
| **Currency** | Code | INR, USD, GBP | Currency code |
| **Payment Mode** | Text | BANK_TRANSFER, CHEQUE | How was it paid? |
| **Contribution Date** | YYYY-MM-DD | 2025-01-15 | When was contribution made |

### Optional Columns:
| Column | Format | Example | Notes |
|--------|--------|---------|-------|
| Exchange Rate | Number | 83.5 | For currency conversion |
| Status | PENDING/COMPLETED | COMPLETED | Payment status |
| Reference Number | Text | TXN001, CHQ123 | Transaction/check number |

---

## Common Issues & Solutions

### "Could not match shareholder"
**Cause:** Shareholder name doesn't match exactly
**Solution:** 
- Check spelling in system
- Use exact first and last name
- Try using First Name + Last Name columns separately

### "Amount is required"
**Cause:** Amount column is empty
**Solution:** Fill in the Amount column with contribution value

### "Invalid date format"
**Cause:** Date not in YYYY-MM-DD format
**Solution:** 
- Change `01/15/2025` to `2025-01-15`
- Use Format Cells → Date in Excel

### "Currency not found"
**Cause:** Invalid currency code
**Solution:** Use valid codes: INR, USD, GBP, EUR, AED, etc.

---

## Advanced: Manual Creation

If you want to manually create the file without the script:

### Using Excel:
1. Create new spreadsheet
2. Add headers in row 1:
   - A1: Stakeholder Name
   - B1: First Name
   - C1: Last Name
   - D1: Contribution Date
   - E1: Amount
   - F1: Currency
   - G1: Payment Mode
   - H1: Status

3. Fill in data starting row 2
4. Save as .xlsx
5. Import via system

### Using CSV:
1. Create new file named `contributions.csv`
2. Add header line:
```
Stakeholder Name,First Name,Last Name,Contribution Date,Amount,Currency,Payment Mode,Status
```
3. Add data lines:
```
Mohammad Sanaullah,Mohammad,Sanaullah,2025-01-15,100000,INR,BANK_TRANSFER,COMPLETED
```
4. Save and import

---

## Batch Import Examples

### Example 1: Import 5 shareholders with different amounts

```
Stakeholder Name,Contribution Date,Amount,Currency,Payment Mode,Status
Mohammad Sanaullah,2025-01-15,100000,INR,BANK_TRANSFER,COMPLETED
Syed Arif,2025-01-16,50000,INR,CHEQUE,PENDING
Mohammad Rafi,2025-01-17,75000,INR,BANK_TRANSFER,COMPLETED
Syed Safi,2025-01-18,60000,INR,BANK_TRANSFER,COMPLETED
Arif Baba,2025-01-19,80000,INR,CASH,COMPLETED
```

### Example 2: Import with different currencies

```
Stakeholder Name,Contribution Date,Amount,Currency,Exchange Rate,Payment Mode,Status
Ansaar Mohammad,2025-01-15,5000,USD,83.5,BANK_TRANSFER,COMPLETED
Shakeel Ahmed,2025-01-16,3000,GBP,105.0,BANK_TRANSFER,COMPLETED
Najaz Saleem,2025-01-17,10000,INR,1.0,BANK_TRANSFER,COMPLETED
```

---

## Tips & Tricks

1. **Start with small batch** - Import 2-3 entries first to verify format
2. **Use Excel for easier editing** - More user-friendly than CSV
3. **Keep reference numbers** - Helps track which transaction
4. **Mark as COMPLETED** - If payment is already received
5. **Use today's date** - Or actual contribution date
6. **Test with one shareholder** - Before bulk importing

---

## Getting Help

**Error during import?**
1. Check the error message for the row number
2. Review that specific row for:
   - Empty cells in required columns
   - Date format (should be YYYY-MM-DD)
   - Currency code validity
3. Fix and try again

**Script not working?**
- Ensure Python is installed
- Run from the project directory
- Check input file path is correct
- Verify file encoding is UTF-8
