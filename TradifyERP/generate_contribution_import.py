"""
Generate Capital Contributions Import File from Shareholder Data

This script helps you create a contribution import file from your shareholder list.
It matches shareholder names and allows you to add contribution amounts.

Usage:
    python generate_contribution_import.py --input shareholders.csv --output contributions.csv
    python generate_contribution_import.py --input shareholders.csv --output contributions.xlsx --format excel
"""

import csv
import openpyxl
from openpyxl.styles import Font, PatternFill
import argparse
from datetime import datetime, date

def generate_contribution_csv(input_file, output_file):
    """Generate CSV for contributions from shareholder list"""
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        shareholders = list(reader)
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        
        # Write header
        writer.writerow([
            'Stakeholder Name',
            'First Name',
            'Last Name',
            'Contribution Date',
            'Amount',
            'Currency',
            'Payment Mode',
            'Status',
            'Exchange Rate',
            'Reference Number'
        ])
        
        # Write data rows with template values
        for sh in shareholders:
            first_name = sh.get('First Name', '').strip()
            last_name = sh.get('Last Name', '').strip()
            full_name = f"{first_name} {last_name}".strip()
            
            writer.writerow([
                full_name,  # Stakeholder Name
                first_name,  # First Name
                last_name,  # Last Name
                datetime.now().strftime('%Y-%m-%d'),  # Contribution Date - TODAY
                '',  # Amount - LEAVE EMPTY TO FILL
                'INR',  # Currency - default to INR
                'BANK_TRANSFER',  # Payment Mode - default
                'COMPLETED',  # Status
                '1.0',  # Exchange Rate
                ''  # Reference Number - optional
            ])
    
    print(f"✅ CSV template created: {output_file}")
    print(f"   Rows: {len(shareholders)} shareholders")
    print(f"\n📝 Instructions:")
    print(f"   1. Open {output_file} in Excel")
    print(f"   2. Fill in the 'Amount' column for each shareholder")
    print(f"   3. Adjust 'Contribution Date' if needed (format: YYYY-MM-DD)")
    print(f"   4. Modify 'Currency' and 'Payment Mode' as needed")
    print(f"   5. Save and import back into the system")

def generate_contribution_excel(input_file, output_file):
    """Generate Excel template for contributions from shareholder list"""
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        shareholders = list(reader)
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Contributions"
    
    # Define header colors
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    
    # Write header
    headers = [
        'Stakeholder Name',
        'First Name',
        'Last Name',
        'Contribution Date',
        'Amount',
        'Currency',
        'Payment Mode',
        'Status',
        'Exchange Rate',
        'Reference Number'
    ]
    ws.append(headers)
    
    # Format header
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
    
    # Add info row
    info_row = 2
    ws[f'A{info_row}'] = "👇 FILL IN AMOUNTS AND DATES BELOW 👇"
    ws.row_dimensions[info_row].height = 20
    ws[f'A{info_row}'].font = Font(italic=True, color="FF0000", size=10)
    
    # Write data rows
    data_start = 3
    for idx, sh in enumerate(shareholders, start=data_start):
        first_name = sh.get('First Name', '').strip()
        last_name = sh.get('Last Name', '').strip()
        full_name = f"{first_name} {last_name}".strip()
        
        ws[f'A{idx}'] = full_name
        ws[f'B{idx}'] = first_name
        ws[f'C{idx}'] = last_name
        ws[f'D{idx}'] = datetime.now().strftime('%Y-%m-%d')
        ws[f'E{idx}'] = None  # Amount - TO BE FILLED
        ws[f'F{idx}'] = 'INR'
        ws[f'G{idx}'] = 'BANK_TRANSFER'
        ws[f'H{idx}'] = 'COMPLETED'
        ws[f'I{idx}'] = 1.0
        ws[f'J{idx}'] = None
    
    # Set column widths
    ws.column_dimensions['A'].width = 25  # Stakeholder Name
    ws.column_dimensions['B'].width = 15  # First Name
    ws.column_dimensions['C'].width = 15  # Last Name
    ws.column_dimensions['D'].width = 18  # Contribution Date
    ws.column_dimensions['E'].width = 15  # Amount
    ws.column_dimensions['F'].width = 12  # Currency
    ws.column_dimensions['G'].width = 18  # Payment Mode
    ws.column_dimensions['H'].width = 12  # Status
    ws.column_dimensions['I'].width = 15  # Exchange Rate
    ws.column_dimensions['J'].width = 18  # Reference Number
    
    # Freeze header row
    ws.freeze_panes = 'A2'
    
    # Save
    wb.save(output_file)
    
    print(f"✅ Excel template created: {output_file}")
    print(f"   Rows: {len(shareholders)} shareholders")
    print(f"\n📝 Instructions:")
    print(f"   1. Open {output_file} in Excel")
    print(f"   2. Fill in the 'Amount' column (column E) for each shareholder")
    print(f"   3. Adjust 'Contribution Date' if needed (format: YYYY-MM-DD)")
    print(f"   4. Modify 'Currency' and 'Payment Mode' as needed")
    print(f"   5. Save and import into the system via Capital Contributions page")

def main():
    parser = argparse.ArgumentParser(
        description='Generate contribution import templates from shareholder data'
    )
    parser.add_argument(
        '--input',
        required=True,
        help='Input CSV file with shareholders (exported from system)'
    )
    parser.add_argument(
        '--output',
        required=True,
        help='Output file for contribution template'
    )
    parser.add_argument(
        '--format',
        choices=['csv', 'excel'],
        default='csv',
        help='Output format (default: csv)'
    )
    
    args = parser.parse_args()
    
    try:
        if args.format == 'excel':
            generate_contribution_excel(args.input, args.output)
        else:
            generate_contribution_csv(args.input, args.output)
        
        print("\n✅ Done! Now edit the file and fill in contribution amounts.")
        print("\n📌 Column Guide:")
        print("   Stakeholder Name: Full name (matches shareholder in system)")
        print("   Amount: Contribution amount (REQUIRED - fill this in!)")
        print("   Currency: INR, USD, GBP, etc.")
        print("   Payment Mode: BANK_TRANSFER, CHEQUE, CASH, etc.")
        print("   Contribution Date: YYYY-MM-DD format")
        print("   Status: PENDING or COMPLETED")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("   Make sure your input file exists and is in the correct location")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    main()
