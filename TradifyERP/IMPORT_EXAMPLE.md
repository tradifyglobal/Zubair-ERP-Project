# Your Data Import Example

Based on your shareholder list, here's exactly how to import contributions:

## Your Shareholders:
```
ID  First Name   Last Name      Email
48  Mohammad     Sanaullah      mohammad...
49  Syed         Arif           arif...
50  Mohammad     Rafi           rafeesmith...
51  Syed         Safi           sam@trac...
52  Imteyazuddin Mohammad       find.same...
53  Fayazuddin   Mohammad       mohammadi...
54  Nazrullah    Shiekhmuhammad nazrullas...
55  Arif         Baba           arifuddin...
56  Ahsan        Ali Khan       murahsans...
57  Aijaz        Sa             aijaz_sa@...
58  Jaiveed      Baba           alpha.whe...
59  Ansaar       Mohammad       ansaar.kh...
60  Mohammad     Kaleem         mkaleemi...
61  Dr. Irfan    Mohammad       irfan@cor...
62  Shakeel      Ahmed          shakeel@...
63  Saiaz        Ahmed          Saiaz@cor...
64  Mohammad     Abdul Malik    mdmanna...
65  Moid         Ali Khan       moidaikh...
66  SHAIK        Burhanuddin    shaikburh...
```

## Step 1: Export Your Shareholders
Go to **Shareholders** page → Click **Export** → Download as CSV

## Step 2: Generate Template
Run this command in PowerShell (from project directory):

```powershell
python generate_contribution_import.py --input shareholders.csv --output my_contributions.xlsx --format excel
```

This creates a file with all your shareholder names pre-filled.

## Step 3: Fill in the Amounts

Open `my_contributions.xlsx` in Excel and fill in the Amount column:

| Stakeholder Name     | First Name | Last Name | Contribution Date | **Amount** | Currency | Payment Mode    | Status    |
|-------------------|-----------|-----------|------------------|--------|----------|-----------------|-----------|
| Mohammad Sanaullah | Mohammad  | Sanaullah | 2025-12-01        | **100000** | INR      | BANK_TRANSFER   | COMPLETED |
| Syed Arif          | Syed      | Arif      | 2025-12-01        | **50000**  | INR      | CHEQUE          | PENDING   |
| Mohammad Rafi      | Mohammad  | Rafi      | 2025-12-01        | **75000**  | INR      | BANK_TRANSFER   | COMPLETED |
| Syed Safi          | Syed      | Safi      | 2025-12-01        | **60000**  | INR      | BANK_TRANSFER   | COMPLETED |
| (and so on...)     |           |           |                   |        |          |                 |           |

You can also modify:
- **Contribution Date** - When was this contribution made?
- **Currency** - Change if needed (default is INR)
- **Payment Mode** - How was it paid? (BANK_TRANSFER, CHEQUE, CASH, etc.)
- **Status** - PENDING (not received yet) or COMPLETED (already received)

## Step 4: Import into System

1. Save your Excel file
2. Go to **Capital Contributions** page
3. Click **Import** button
4. Select your filled Excel file
5. Click **Import**

**Result:** System automatically:
- ✅ Finds each shareholder by name
- ✅ Creates contribution records
- ✅ Updates "Total Invested" for each shareholder
- ✅ Shows success message with count

---

## Example Import File (Ready to Use)

Copy this and save as `sample_contributions.csv` to test:

```csv
Stakeholder Name,First Name,Last Name,Contribution Date,Amount,Currency,Payment Mode,Status
Mohammad Sanaullah,Mohammad,Sanaullah,2025-01-15,100000,INR,BANK_TRANSFER,COMPLETED
Syed Arif,Syed,Arif,2025-01-16,50000,INR,CHEQUE,PENDING
Mohammad Rafi,Mohammad,Rafi,2025-01-17,75000,INR,BANK_TRANSFER,COMPLETED
Syed Safi,Syed,Safi,2025-01-18,60000,INR,BANK_TRANSFER,COMPLETED
Imteyazuddin Mohammad,Imteyazuddin,Mohammad,2025-01-19,85000,INR,BANK_TRANSFER,COMPLETED
Fayazuddin Mohammad,Fayazuddin,Mohammad,2025-01-20,120000,INR,BANK_TRANSFER,COMPLETED
Nazrullah Shiekhmuhammad,Nazrullah,Shiekhmuhammad,2025-01-21,95000,INR,BANK_TRANSFER,PENDING
Arif Baba,Arif,Baba,2025-01-22,40000,INR,CHEQUE,COMPLETED
Ahsan Ali Khan,Ahsan,Ali Khan,2025-01-23,70000,INR,BANK_TRANSFER,COMPLETED
Aijaz Sa,Aijaz,Sa,2025-01-24,55000,INR,BANK_TRANSFER,COMPLETED
```

Then go to **Capital Contributions** → **Import** → Select this file → Done!

---

## What Happens After Import

1. **Each shareholder gets their contribution recorded**
   - Mohammad Sanaullah: 100,000 INR contribution created
   - Syed Arif: 50,000 INR contribution created
   - (etc. for all rows)

2. **Total Invested automatically updates**
   - View shareholder detail page
   - See total invested increased
   - Status badge shows COMPLETED/PENDING

3. **You can see all contributions**
   - Go to Capital Contributions list
   - Filter by shareholder
   - Export or edit as needed

---

## Need Different Amounts?

Simply modify the **Amount** column:

```
Mohammad Sanaullah, ..., 500000
Syed Arif, ..., 250000
...
```

Each value becomes their contribution amount.

---

## Troubleshooting

**"Could not match shareholder"**
- Make sure names in file match exactly in system
- Check spelling

**"Amount is required"**
- Fill in the Amount column - can't import without it

**"Invalid date format"**
- Use YYYY-MM-DD format
- Example: 2025-01-15 ✅, 01/15/2025 ❌

**Import shows partial success**
- Some rows imported, others had errors
- Check error message for which rows failed
- Fix those specific rows and re-import

---

## Quick Reference

| What You Want | How to Do It |
|---------------|------------|
| Import 66 shareholders with contributions | Use the `generate_contribution_import.py` script |
| Fill in amounts easily | Use Excel template format |
| Import with currency conversion | Add Exchange Rate column |
| Mark as pending payment | Set Status to PENDING |
| See all contributions after import | Go to Capital Contributions page |
| Fix a mistake | Export, edit, re-import with overwrite option |
