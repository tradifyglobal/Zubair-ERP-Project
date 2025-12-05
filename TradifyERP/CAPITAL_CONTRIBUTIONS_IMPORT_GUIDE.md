# Capital Contributions Bulk Import Guide

## Overview
You can now bulk import capital contributions for shareholders by matching them to shareholder names. The import feature supports both CSV and Excel files and can match contributions using shareholder name OR shareholder ID.

## How to Use

### 1. Access the Import Feature
- Navigate to **Shareholders > Capital Contributions** page
- Click the **Import** button (top right)
- Select your CSV or Excel file
- Choose whether to overwrite existing entries
- Click **Import**

### 2. Prepare Your Import File

#### Required Columns:
- **Contribution Date** - YYYY-MM-DD format (e.g., 2025-01-15)
- **Amount** - Numeric value (e.g., 100000)
- **Currency** - Currency code (e.g., INR, USD)
- **Payment Mode** - e.g., BANK_TRANSFER, CASH, CHEQUE

#### Optional Columns:
- **Status** - PENDING or COMPLETED (defaults to PENDING)
- **Reference Number** - e.g., check/transaction number
- **Exchange Rate** - Conversion rate (defaults to 1.0)

#### Shareholder Matching (choose ONE):
Option 1: **Stakeholder ID** (exact match)
- Use the shareholder's database ID

Option 2: **Stakeholder Name** (case-insensitive)
- Full name in format: "First Last"
- Example: "John Smith"

Option 3: **First Name + Last Name** (separate columns, case-insensitive)
- "First Name" column
- "Last Name" column

### 3. CSV Example

```csv
Stakeholder Name,Contribution Date,Amount,Currency,Payment Mode,Status,Exchange Rate,Reference Number
John Smith,2025-01-15,100000,INR,BANK_TRANSFER,COMPLETED,1.0,TXN001
Jane Doe,2025-01-16,50000,USD,CHEQUE,PENDING,83.5,CHQ002
```

### 4. Excel Example

| Stakeholder Name | Contribution Date | Amount  | Currency | Payment Mode    | Status    | Exchange Rate | Reference Number |
|------------------|------------------|---------|----------|-----------------|-----------|---------------|-----------------|
| John Smith       | 2025-01-15       | 100000  | INR      | BANK_TRANSFER   | COMPLETED | 1.0           | TXN001          |
| Jane Doe         | 2025-01-16       | 50000   | USD      | CHEQUE          | PENDING   | 83.5          | CHQ002          |

## Matching Rules

The import process attempts to match shareholders in this order:

1. **By Stakeholder ID** (if provided and found)
2. **By Stakeholder Name** (if provided and matches exactly)
3. **By First Name + Last Name** (if both columns provided)

### Example Matching

| Import Data | Matches To | Status |
|------------|-----------|--------|
| ID: 5, Name: "John Smith" | Stakeholder with ID 5 | ✅ Found by ID |
| ID: 999, Name: "John Smith" | Stakeholder named John Smith | ✅ Found by name (ID not found) |
| Name: "john smith" | Stakeholder named John Smith | ✅ Found (case-insensitive) |
| Name: "smith john" | Not found | ❌ Name order matters |

## Import Process

### On Success:
- Contributions are created/updated in the system
- Each shareholder's total invested amount is automatically recalculated
- Success message shows number of contributions imported

### On Error:
- Specific row numbers and error messages are displayed
- You can correct the file and try again
- Partially successful imports still create valid entries

## Error Messages & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| "Contribution Date, Amount, Currency, and Payment Mode are required" | Missing required column or value | Ensure all required columns have values |
| "Could not match shareholder" | Shareholder name not found | Check spelling and use exact format |
| "Currency INR not found" | Invalid currency code | Use valid currency codes (INR, USD, GBP, etc.) |
| "Invalid date format. Use YYYY-MM-DD" | Date in wrong format | Format dates as YYYY-MM-DD |
| "Invalid amount or exchange rate format" | Non-numeric value | Use numbers only, no currency symbols |

## Tips

1. **Use Shareholder Name for simplicity** - No need to look up IDs
2. **Match case-insensitive** - "john smith", "John Smith", "JOHN SMITH" all work
3. **Double-check dates** - Use YYYY-MM-DD format only
4. **Test with small batch first** - Import 2-3 entries to verify format
5. **Export first, then edit** - Export existing contributions as template

## Bulk Operations

### To Import Multiple Files:
1. Import File 1 - X contributions created
2. Import File 2 - Y more contributions created
3. Continue as needed

### To Update Existing Contributions:
1. Export current contributions
2. Edit the Amount/Date/Status in Excel
3. Check "Overwrite existing" checkbox
4. Import the modified file
5. Contributions with matching ID are updated

## Support

For issues during import:
1. Check error messages for specific row numbers
2. Verify currency codes are valid
3. Ensure shareholder names match exactly in system
4. Try importing one entry at a time to isolate issues
