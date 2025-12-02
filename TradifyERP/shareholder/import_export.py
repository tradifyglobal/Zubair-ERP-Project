import csv
import io
from django.http import HttpResponse
from accounting.models import Stakeholder, Entity
import openpyxl
from openpyxl.utils import get_column_letter


def export_shareholders_csv(stakeholders):
    """Export shareholders to CSV format"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'ID', 'First Name', 'Last Name', 'Email', 'Phone Number', 
        'Address Line 1', 'City', 'State/Province', 'Postal Code', 'Country'
    ])
    
    # Write data
    for stakeholder in stakeholders:
        writer.writerow([
            stakeholder.id,
            stakeholder.first_name or '',
            stakeholder.last_name or '',
            stakeholder.email or '',
            str(stakeholder.phone_number or ''),  # Convert to text
            stakeholder.address_line_1 or '',
            stakeholder.city or '',
            stakeholder.state_province or '',
            stakeholder.postal_code or '',
            stakeholder.country or '',
        ])
    
    # Create HTTP response
    response = HttpResponse(output.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="shareholders.csv"'
    return response


def export_shareholders_excel(stakeholders):
    """Export shareholders to Excel format"""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Shareholders"
    
    # Write header
    headers = ['ID', 'First Name', 'Last Name', 'Email', 'Phone Number', 
               'Address Line 1', 'City', 'State/Province', 'Postal Code', 'Country']
    ws.append(headers)
    
    # Style header
    from openpyxl.styles import Font, PatternFill
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
    
    # Write data
    for stakeholder in stakeholders:
        ws.append([
            stakeholder.id,
            stakeholder.first_name or '',
            stakeholder.last_name or '',
            stakeholder.email or '',
            str(stakeholder.phone_number or ''),  # Convert to text
            stakeholder.address_line_1 or '',
            stakeholder.city or '',
            stakeholder.state_province or '',
            stakeholder.postal_code or '',
            stakeholder.country or '',
        ])
    
    # Auto-adjust column widths
    for column in ws.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width
    
    # Format Phone Number column as text
    phone_col = get_column_letter(headers.get('Phone Number', 5))
    for row_num in range(2, ws.max_row + 1):
        cell = ws[f'{phone_col}{row_num}']
        cell.number_format = '@'  # Text format in Excel
    
    # Create HTTP response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="shareholders.xlsx"'
    wb.save(response)
    return response


def import_shareholders_csv(file_content, entity, overwrite=False):
    """Import shareholders from CSV file"""
    errors = []
    imported_count = 0
    
    try:
        text_stream = io.StringIO(file_content.read().decode('utf-8'))
        reader = csv.DictReader(text_stream)
        
        for row_num, row in enumerate(reader, start=2):
            try:
                # Extract data
                first_name = row.get('First Name', '').strip()
                last_name = row.get('Last Name', '').strip()
                email = row.get('Email', '').strip()
                phone_number = str(row.get('Phone Number', '').strip())  # Convert to text
                
                # Validate required fields
                if not first_name or not last_name or not email:
                    errors.append(f"Row {row_num}: First name, last name, and email are required")
                    continue
                
                # Get or create stakeholder
                stakeholder_id = row.get('ID', '').strip()
                
                if stakeholder_id and overwrite:
                    try:
                        stakeholder = Stakeholder.objects.get(id=int(stakeholder_id), entity=entity)
                        stakeholder.first_name = first_name
                        stakeholder.last_name = last_name
                        stakeholder.email = email
                        stakeholder.phone_number = phone_number
                        stakeholder.address_line_1 = row.get('Address Line 1', '').strip() or ''
                        stakeholder.city = row.get('City', '').strip() or ''
                        stakeholder.state_province = row.get('State/Province', '').strip() or ''
                        stakeholder.postal_code = row.get('Postal Code', '').strip() or ''
                        stakeholder.country = row.get('Country', '').strip() or ''
                        stakeholder.save()
                        imported_count += 1
                    except Stakeholder.DoesNotExist:
                        errors.append(f"Row {row_num}: Stakeholder with ID {stakeholder_id} not found")
                        continue
                else:
                    stakeholder = Stakeholder.objects.create(
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        phone_number=phone_number,
                        address_line_1=row.get('Address Line 1', '').strip() or '',
                        city=row.get('City', '').strip() or '',
                        state_province=row.get('State/Province', '').strip() or '',
                        postal_code=row.get('Postal Code', '').strip() or '',
                        country=row.get('Country', '').strip() or '',
                        entity=entity,
                        stakeholder_type='INDIVIDUAL'
                    )
                    imported_count += 1
            
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
    except Exception as e:
        errors.append(f"Error reading file: {str(e)}")
    
    return imported_count, errors


def import_shareholders_excel(file_content, entity, overwrite=False):
    """Import shareholders from Excel file"""
    errors = []
    imported_count = 0
    
    try:
        wb = openpyxl.load_workbook(file_content)
        ws = wb.active
        
        # Get header row
        headers = {}
        for col_num, cell in enumerate(ws[1], start=1):
            if cell.value:
                headers[cell.value] = col_num
        
        # Validate required headers
        required_headers = ['First Name', 'Last Name', 'Email']
        for req_header in required_headers:
            if req_header not in headers:
                errors.append(f"Missing required column: {req_header}")
        
        if errors:
            return imported_count, errors
        
        # Import data
        for row_num, row in enumerate(ws.iter_rows(min_row=2, values_only=False), start=2):
            try:
                # Extract values
                first_name = (row[headers['First Name']-1].value or '').strip()
                last_name = (row[headers['Last Name']-1].value or '').strip()
                email = (row[headers['Email']-1].value or '').strip()
                phone_number = str(row[headers.get('Phone Number', 0)-1].value or '').strip() if 'Phone Number' in headers else ''
                
                # Validate required fields
                if not first_name or not last_name or not email:
                    errors.append(f"Row {row_num}: First name, last name, and email are required")
                    continue
                
                # Get optional fields
                address_line_1 = ''
                city = ''
                state_province = ''
                postal_code = ''
                country = ''
                
                if 'Address Line 1' in headers:
                    address_line_1 = (row[headers['Address Line 1']-1].value or '').strip()
                if 'City' in headers:
                    city = (row[headers['City']-1].value or '').strip()
                if 'State/Province' in headers:
                    state_province = (row[headers['State/Province']-1].value or '').strip()
                if 'Postal Code' in headers:
                    postal_code = (row[headers['Postal Code']-1].value or '').strip()
                if 'Country' in headers:
                    country = (row[headers['Country']-1].value or '').strip()
                
                # Check for ID for update
                stakeholder_id = None
                if 'ID' in headers:
                    id_val = row[headers['ID']-1].value
                    if id_val:
                        stakeholder_id = int(id_val)
                
                if stakeholder_id and overwrite:
                    try:
                        stakeholder = Stakeholder.objects.get(id=stakeholder_id, entity=entity)
                        stakeholder.first_name = first_name
                        stakeholder.last_name = last_name
                        stakeholder.email = email
                        stakeholder.phone_number = phone_number
                        stakeholder.address_line_1 = address_line_1 or ''
                        stakeholder.city = city or ''
                        stakeholder.state_province = state_province or ''
                        stakeholder.postal_code = postal_code or ''
                        stakeholder.country = country or ''
                        stakeholder.save()
                        imported_count += 1
                    except Stakeholder.DoesNotExist:
                        errors.append(f"Row {row_num}: Stakeholder with ID {stakeholder_id} not found")
                        continue
                else:
                    stakeholder = Stakeholder.objects.create(
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        phone_number=phone_number,
                        address_line_1=address_line_1 or '',
                        city=city or '',
                        state_province=state_province or '',
                        postal_code=postal_code or '',
                        country=country or '',
                        entity=entity,
                        stakeholder_type='INDIVIDUAL'
                    )
                    imported_count += 1
            
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
    except Exception as e:
        errors.append(f"Error reading Excel file: {str(e)}")
    
    return imported_count, errors
