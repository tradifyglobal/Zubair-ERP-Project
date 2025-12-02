import csv
import io
from django.http import HttpResponse
from accounting.models import Stakeholder, Entity, CapitalContribution, Currency
import openpyxl
from openpyxl.utils import get_column_letter
from datetime import datetime


def export_shareholders_csv(stakeholders):
    """Export shareholders to CSV format"""
    output = io.StringIO()
    # Use QUOTE_ALL to ensure phone numbers are quoted and treated as text in Excel
    writer = csv.writer(output, quoting=csv.QUOTE_ALL)
    
    # Write header
    writer.writerow([
        'ID', 'First Name', 'Last Name', 'Email', 'Phone Number', 
        'Address Line 1', 'City', 'State/Province', 'Postal Code', 'Country'
    ])
    
    # Write data
    for stakeholder in stakeholders:
        writer.writerow([
            str(stakeholder.id),
            stakeholder.first_name or '',
            stakeholder.last_name or '',
            stakeholder.email or '',
            str(stakeholder.phone_number or ''),  # Ensure phone is treated as text
            stakeholder.address_line_1 or '',
            stakeholder.city or '',
            stakeholder.state_province or '',
            stakeholder.postal_code or '',
            stakeholder.country or '',
        ])
    
    # Create HTTP response
    response = HttpResponse(output.getvalue(), content_type='text/csv; charset=utf-8')
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
            stakeholder.phone_number or '',  # Phone number as raw value
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
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width
    
    # Format Phone Number column as text BEFORE writing values
    # Phone Number is column 5 (E)
    phone_col = 'E'
    for row_num in range(2, ws.max_row + 1):
        cell = ws[f'{phone_col}{row_num}']
        # Set as text format
        cell.number_format = '@'
        # Force as string data type by wrapping in str() and setting data_type
        if cell.value:
            cell.data_type = 's'  # 's' = string data type
    
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
                # Convert phone number to string and handle special characters
                phone_value = row.get('Phone Number', '')
                phone_number = str(phone_value).strip() if phone_value else ''
                # Remove leading apostrophe if present (from Excel text formatting)
                if phone_number.startswith("'"):
                    phone_number = phone_number[1:]
                
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
                    except ValueError as ve:
                        errors.append(f"Row {row_num}: Invalid stakeholder ID format - {str(ve)}")
                        continue
                else:
                    try:
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
                        errors.append(f"Row {row_num}: Error creating stakeholder - {str(e)}")
                        continue
            
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
                # Convert phone number to string and handle special characters
                phone_val = row[headers.get('Phone Number')-1].value if 'Phone Number' in headers else None
                phone_number = str(phone_val).strip() if phone_val else ''
                # Remove leading apostrophe if present (from Excel text formatting)
                if phone_number.startswith("'"):
                    phone_number = phone_number[1:]
                
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
                        try:
                            stakeholder_id = int(id_val)
                        except (ValueError, TypeError):
                            pass
                
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
                    except Exception as e:
                        errors.append(f"Row {row_num}: Error updating stakeholder - {str(e)}")
                        continue
                else:
                    try:
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
                        errors.append(f"Row {row_num}: Error creating stakeholder - {str(e)}")
                        continue
            
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
    except Exception as e:
        errors.append(f"Error reading Excel file: {str(e)}")
    
    return imported_count, errors


# ==================== Capital Contribution Export/Import ====================

def export_capital_contributions_csv(contributions):
    """Export capital contributions to CSV format"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'ID', 'Stakeholder ID', 'Stakeholder Name', 'Contribution Date', 'Amount', 
        'Currency', 'Status', 'Payment Mode', 'Reference Number', 'Exchange Rate'
    ])
    
    # Write data
    for contrib in contributions:
        writer.writerow([
            contrib.id,
            contrib.stakeholder.id,
            f"{contrib.stakeholder.first_name} {contrib.stakeholder.last_name}",
            contrib.contribution_date.strftime('%Y-%m-%d'),
            str(contrib.amount),
            contrib.currency.code,
            contrib.status,
            contrib.payment_mode,
            contrib.reference_number or '',
            str(contrib.exchange_rate),
        ])
    
    # Create HTTP response
    response = HttpResponse(output.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="capital_contributions.csv"'
    return response


def export_capital_contributions_excel(contributions):
    """Export capital contributions to Excel format"""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Contributions"
    
    # Write header
    headers = ['ID', 'Stakeholder ID', 'Stakeholder Name', 'Contribution Date', 'Amount', 
               'Currency', 'Status', 'Payment Mode', 'Reference Number', 'Exchange Rate']
    ws.append(headers)
    
    # Style header
    from openpyxl.styles import Font, PatternFill
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
    
    # Write data
    for contrib in contributions:
        ws.append([
            contrib.id,
            contrib.stakeholder.id,
            f"{contrib.stakeholder.first_name} {contrib.stakeholder.last_name}",
            contrib.contribution_date.strftime('%Y-%m-%d'),
            float(contrib.amount),
            contrib.currency.code,
            contrib.status,
            contrib.payment_mode,
            contrib.reference_number or '',
            float(contrib.exchange_rate),
        ])
    
    # Auto-adjust column widths
    for column in ws.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width
    
    # Create HTTP response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="capital_contributions.xlsx"'
    wb.save(response)
    return response


def import_capital_contributions_csv(file_content, entity, overwrite=False):
    """Import capital contributions from CSV file - matches by Stakeholder Name or ID"""
    errors = []
    imported_count = 0
    
    try:
        text_stream = io.StringIO(file_content.read().decode('utf-8'))
        reader = csv.DictReader(text_stream)
        
        for row_num, row in enumerate(reader, start=2):
            try:
                # Extract data - try to get stakeholder by ID or Name
                stakeholder_id = row.get('Stakeholder ID', '').strip()
                stakeholder_name = row.get('Stakeholder Name', '').strip()
                first_name = row.get('First Name', '').strip()
                last_name = row.get('Last Name', '').strip()
                
                contribution_date = row.get('Contribution Date', '').strip()
                amount = row.get('Amount', '').strip()
                currency_code = row.get('Currency', '').strip()
                status = row.get('Status', 'PENDING').strip()
                payment_mode = row.get('Payment Mode', '').strip()
                reference_number = row.get('Reference Number', '').strip()
                exchange_rate = row.get('Exchange Rate', '1.0').strip()
                
                # Validate required fields
                if not contribution_date or not amount or not currency_code or not payment_mode:
                    errors.append(f"Row {row_num}: Contribution Date, Amount, Currency, and Payment Mode are required")
                    continue
                
                # Get stakeholder by ID first, then by name
                stakeholder = None
                if stakeholder_id:
                    try:
                        stakeholder = Stakeholder.objects.get(id=int(stakeholder_id), entity=entity)
                    except (Stakeholder.DoesNotExist, ValueError):
                        pass
                
                if not stakeholder and stakeholder_name:
                    # Try to match full name
                    parts = stakeholder_name.split()
                    if len(parts) >= 2:
                        first = ' '.join(parts[:-1])
                        last = parts[-1]
                        try:
                            stakeholder = Stakeholder.objects.get(first_name__iexact=first, last_name__iexact=last, entity=entity)
                        except Stakeholder.DoesNotExist:
                            pass
                
                if not stakeholder and first_name and last_name:
                    try:
                        stakeholder = Stakeholder.objects.get(first_name__iexact=first_name, last_name__iexact=last_name, entity=entity)
                    except Stakeholder.DoesNotExist:
                        pass
                
                if not stakeholder:
                    errors.append(f"Row {row_num}: Could not match shareholder. Provide either Stakeholder ID or Stakeholder Name (First Last)")
                    continue
                
                # Get currency
                try:
                    currency = Currency.objects.get(code=currency_code)
                except Currency.DoesNotExist:
                    errors.append(f"Row {row_num}: Currency {currency_code} not found")
                    continue
                
                # Get company currency
                company_currency = entity.company_currency or Currency.objects.filter(code='INR').first()
                if not company_currency:
                    errors.append(f"Row {row_num}: Company currency not found")
                    continue
                
                # Parse date
                try:
                    contrib_date = datetime.strptime(contribution_date, '%Y-%m-%d').date()
                except ValueError:
                    errors.append(f"Row {row_num}: Invalid date format. Use YYYY-MM-DD")
                    continue
                
                # Parse amount and exchange rate
                try:
                    amount_val = float(amount)
                    exchange_rate_val = float(exchange_rate)
                except ValueError:
                    errors.append(f"Row {row_num}: Invalid amount or exchange rate format")
                    continue
                
                # Calculate company currency amount
                amount_company_currency = amount_val * exchange_rate_val
                
                # Check ID for update
                contrib_id = None
                try:
                    contrib_id_str = row.get('ID', '').strip()
                    if contrib_id_str:
                        contrib_id = int(contrib_id_str)
                except ValueError:
                    pass
                
                if contrib_id and overwrite:
                    try:
                        contribution = CapitalContribution.objects.get(id=contrib_id, entity=entity)
                        contribution.stakeholder = stakeholder
                        contribution.contribution_date = contrib_date
                        contribution.amount = amount_val
                        contribution.currency = currency
                        contribution.currency_destination = company_currency
                        contribution.exchange_rate = exchange_rate_val
                        contribution.amount_company_currency = amount_company_currency
                        contribution.status = status
                        contribution.payment_mode = payment_mode
                        contribution.reference_number = reference_number or None
                        contribution.save()
                        imported_count += 1
                    except CapitalContribution.DoesNotExist:
                        errors.append(f"Row {row_num}: Capital contribution with ID {contrib_id} not found")
                        continue
                else:
                    contribution = CapitalContribution.objects.create(
                        entity=entity,
                        stakeholder=stakeholder,
                        contribution_date=contrib_date,
                        amount=amount_val,
                        currency=currency,
                        currency_destination=company_currency,
                        exchange_rate=exchange_rate_val,
                        amount_company_currency=amount_company_currency,
                        amount_usd=0,  # Will be calculated if needed
                        status=status,
                        payment_mode=payment_mode,
                        reference_number=reference_number or None,
                    )
                    imported_count += 1
            
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
    except Exception as e:
        errors.append(f"Error reading file: {str(e)}")
    
    return imported_count, errors


def import_capital_contributions_excel(file_content, entity, overwrite=False):
    """Import capital contributions from Excel file - matches by Stakeholder Name or ID"""
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
        
        # Validate required headers - only need contribution details, stakeholder match is flexible
        required_headers = ['Contribution Date', 'Amount', 'Currency', 'Payment Mode']
        for req_header in required_headers:
            if req_header not in headers:
                errors.append(f"Missing required column: {req_header}")
        
        if errors:
            return imported_count, errors
        
        # Import data
        for row_num, row in enumerate(ws.iter_rows(min_row=2, values_only=False), start=2):
            try:
                # Extract stakeholder identifiers
                stakeholder_id_val = row[headers['Stakeholder ID']-1].value if 'Stakeholder ID' in headers else None
                stakeholder_name_val = row[headers['Stakeholder Name']-1].value if 'Stakeholder Name' in headers else None
                first_name_val = row[headers['First Name']-1].value if 'First Name' in headers else None
                last_name_val = row[headers['Last Name']-1].value if 'Last Name' in headers else None
                
                # Extract contribution data
                contribution_date_val = row[headers['Contribution Date']-1].value
                amount_val = row[headers['Amount']-1].value
                currency_code_val = row[headers['Currency']-1].value
                payment_mode_val = row[headers['Payment Mode']-1].value
                status_val = (row[headers['Status']-1].value if 'Status' in headers else 'PENDING') or 'PENDING'
                reference_number_val = (row[headers['Reference Number']-1].value or '') if 'Reference Number' in headers else ''
                exchange_rate_val = (row[headers['Exchange Rate']-1].value or 1.0) if 'Exchange Rate' in headers else 1.0
                
                # Validate required contribution fields
                if not contribution_date_val or not amount_val or not currency_code_val or not payment_mode_val:
                    errors.append(f"Row {row_num}: Contribution Date, Amount, Currency, and Payment Mode are required")
                    continue
                
                # Get stakeholder by ID first, then by name
                stakeholder = None
                if stakeholder_id_val:
                    try:
                        stakeholder = Stakeholder.objects.get(id=int(stakeholder_id_val), entity=entity)
                    except (Stakeholder.DoesNotExist, ValueError, TypeError):
                        pass
                
                if not stakeholder and stakeholder_name_val:
                    # Try to match full name
                    parts = str(stakeholder_name_val).split()
                    if len(parts) >= 2:
                        first = ' '.join(parts[:-1])
                        last = parts[-1]
                        try:
                            stakeholder = Stakeholder.objects.get(first_name__iexact=first, last_name__iexact=last, entity=entity)
                        except Stakeholder.DoesNotExist:
                            pass
                
                if not stakeholder and first_name_val and last_name_val:
                    try:
                        stakeholder = Stakeholder.objects.get(first_name__iexact=str(first_name_val), last_name__iexact=str(last_name_val), entity=entity)
                    except Stakeholder.DoesNotExist:
                        pass
                
                if not stakeholder:
                    errors.append(f"Row {row_num}: Could not match shareholder. Provide either Stakeholder ID, Stakeholder Name, or First Name + Last Name")
                    continue
                
                # Get currency
                try:
                    currency = Currency.objects.get(code=str(currency_code_val))
                except Currency.DoesNotExist:
                    errors.append(f"Row {row_num}: Currency {currency_code_val} not found")
                    continue
                
                # Get company currency
                company_currency = entity.company_currency or Currency.objects.filter(code='INR').first()
                if not company_currency:
                    errors.append(f"Row {row_num}: Company currency not found")
                    continue
                
                # Parse date
                try:
                    if isinstance(contribution_date_val, str):
                        contrib_date = datetime.strptime(contribution_date_val, '%Y-%m-%d').date()
                    else:
                        contrib_date = contribution_date_val
                except (ValueError, TypeError):
                    errors.append(f"Row {row_num}: Invalid date format. Use YYYY-MM-DD")
                    continue
                
                # Parse amounts
                try:
                    amount_numeric = float(amount_val)
                    exchange_rate_numeric = float(exchange_rate_val) if exchange_rate_val else 1.0
                except (ValueError, TypeError):
                    errors.append(f"Row {row_num}: Invalid amount or exchange rate format")
                    continue
                
                # Calculate company currency amount
                amount_company_currency = amount_numeric * exchange_rate_numeric
                
                # Check ID for update
                contrib_id = None
                if 'ID' in headers:
                    id_val = row[headers['ID']-1].value
                    if id_val:
                        try:
                            contrib_id = int(id_val)
                        except (ValueError, TypeError):
                            pass
                
                if contrib_id and overwrite:
                    try:
                        contribution = CapitalContribution.objects.get(id=contrib_id, entity=entity)
                        contribution.stakeholder = stakeholder
                        contribution.contribution_date = contrib_date
                        contribution.amount = amount_numeric
                        contribution.currency = currency
                        contribution.currency_destination = company_currency
                        contribution.exchange_rate = exchange_rate_numeric
                        contribution.amount_company_currency = amount_company_currency
                        contribution.status = status_val
                        contribution.payment_mode = payment_mode_val
                        contribution.reference_number = reference_number_val or None
                        contribution.save()
                        imported_count += 1
                    except CapitalContribution.DoesNotExist:
                        errors.append(f"Row {row_num}: Capital contribution with ID {contrib_id} not found")
                        continue
                else:
                    contribution = CapitalContribution.objects.create(
                        entity=entity,
                        stakeholder=stakeholder,
                        contribution_date=contrib_date,
                        amount=amount_numeric,
                        currency=currency,
                        currency_destination=company_currency,
                        exchange_rate=exchange_rate_numeric,
                        amount_company_currency=amount_company_currency,
                        amount_usd=0,  # Will be calculated if needed
                        status=status_val,
                        payment_mode=payment_mode_val,
                        reference_number=reference_number_val or None,
                    )
                    imported_count += 1
            
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
    except Exception as e:
        errors.append(f"Error reading Excel file: {str(e)}")
    
    return imported_count, errors
