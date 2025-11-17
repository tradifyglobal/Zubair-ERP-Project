"""
Django management command to populate sample sales data.
Creates sample customers, invoices, and records payments.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from sales.models import Customer, SalesOrder, SalesOrderLine, Invoice
from accounting.models import Entity, Account


class Command(BaseCommand):
    help = 'Populate sample sales data for testing P&L reporting'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting sample data population...'))

        # Get or create default entity
        try:
            entity = Entity.objects.get(code='TRADIFY-001')
        except Entity.DoesNotExist:
            self.stdout.write(self.style.ERROR('Entity TRADIFY-001 not found. Please create it first.'))
            return

        # Sample customers
        customers_data = [
            {
                'customer_code': 'CUST-001',
                'customer_name': 'Acme Corporation',
                'email': 'contact@acme.com',
                'phone': '+1-800-ACME-001',
                'billing_address': '123 Business Street, New York, NY 10001',
                'city': 'New York',
                'state': 'NY',
                'postal_code': '10001',
                'country': 'USA',
                'customer_type': 'BUSINESS',
            },
            {
                'customer_code': 'CUST-002',
                'customer_name': 'TechStart Inc',
                'email': 'info@techstart.com',
                'phone': '+1-415-TECH-123',
                'billing_address': '456 Innovation Drive, San Francisco, CA 94105',
                'city': 'San Francisco',
                'state': 'CA',
                'postal_code': '94105',
                'country': 'USA',
                'customer_type': 'BUSINESS',
            },
            {
                'customer_code': 'CUST-003',
                'customer_name': 'Global Enterprises Ltd',
                'email': 'sales@global-ent.com',
                'phone': '+44-20-GLOB-456',
                'billing_address': '789 Commerce Plaza, London, UK W1A 1AA',
                'city': 'London',
                'state': 'England',
                'postal_code': 'W1A 1AA',
                'country': 'UK',
                'customer_type': 'BUSINESS',
            },
            {
                'customer_code': 'CUST-004',
                'customer_name': 'StartUp Ventures',
                'email': 'hello@startupvent.com',
                'phone': '+1-650-STARTUP',
                'billing_address': '321 Innovation Way, Palo Alto, CA 94301',
                'city': 'Palo Alto',
                'state': 'CA',
                'postal_code': '94301',
                'country': 'USA',
                'customer_type': 'BUSINESS',
            },
        ]

        # Create customers
        customers = []
        for idx, cust_data in enumerate(customers_data, 1):
            customer, created = Customer.objects.update_or_create(
                customer_code=cust_data['customer_code'],
                defaults={
                    'entity': entity,
                    'customer_name': cust_data['customer_name'],
                    'customer_type': cust_data['customer_type'],
                    'email': cust_data['email'],
                    'phone': cust_data['phone'],
                    'billing_address': cust_data['billing_address'],
                    'city': cust_data['city'],
                    'state': cust_data['state'],
                    'postal_code': cust_data['postal_code'],
                    'country': cust_data['country'],
                    'status': 'ACTIVE',
                }
            )
            customers.append(customer)
            status = "Created" if created else "Updated"
            self.stdout.write(
                self.style.SUCCESS(f'  [OK] {status}: {customer.customer_name}')
            )

        # Sample invoice data
        invoice_data = [
            # Invoice 1: Large order, fully paid
            {
                'customer': customers[0],
                'subtotal': Decimal('5000.00'),
                'tax_percent': Decimal('10'),
                'status': 'PAID',
                'amount_paid': Decimal('5500.00'),
                'days_ago': 25,
            },
            # Invoice 2: Medium order, partially paid
            {
                'customer': customers[1],
                'subtotal': Decimal('2500.00'),
                'tax_percent': Decimal('10'),
                'status': 'PARTIAL',
                'amount_paid': Decimal('1375.00'),
                'days_ago': 15,
            },
            # Invoice 3: Small order, not paid
            {
                'customer': customers[2],
                'subtotal': Decimal('1000.00'),
                'tax_percent': Decimal('10'),
                'status': 'ISSUED',
                'amount_paid': Decimal('0.00'),
                'days_ago': 10,
            },
            # Invoice 4: Large order, fully paid
            {
                'customer': customers[3],
                'subtotal': Decimal('7500.00'),
                'tax_percent': Decimal('10'),
                'status': 'PAID',
                'amount_paid': Decimal('8250.00'),
                'days_ago': 8,
            },
            # Invoice 5: Medium order, issued today
            {
                'customer': customers[0],
                'subtotal': Decimal('3200.00'),
                'tax_percent': Decimal('10'),
                'status': 'ISSUED',
                'amount_paid': Decimal('0.00'),
                'days_ago': 0,
            },
            # Invoice 6: Small order, fully paid
            {
                'customer': customers[1],
                'subtotal': Decimal('800.00'),
                'tax_percent': Decimal('10'),
                'status': 'PAID',
                'amount_paid': Decimal('880.00'),
                'days_ago': 5,
            },
            # Invoice 7: Medium order, partially paid
            {
                'customer': customers[2],
                'subtotal': Decimal('4200.00'),
                'tax_percent': Decimal('10'),
                'status': 'PARTIAL',
                'amount_paid': Decimal('2310.00'),
                'days_ago': 3,
            },
            # Invoice 8: Large order, issued recently
            {
                'customer': customers[3],
                'subtotal': Decimal('6000.00'),
                'tax_percent': Decimal('10'),
                'status': 'ISSUED',
                'amount_paid': Decimal('0.00'),
                'days_ago': 2,
            },
        ]

        # Create sample sales orders first (required for invoices)
        sample_orders = []
        for idx, inv_data in enumerate(invoice_data, 1):
            order_date = timezone.now() - timedelta(days=inv_data['days_ago'])
            tax_amount = (inv_data['subtotal'] * inv_data['tax_percent']) / 100
            total_amount = inv_data['subtotal'] + tax_amount
            
            sales_order, created = SalesOrder.objects.update_or_create(
                so_number=f'SO-2025-{100 + idx:03d}',
                defaults={
                    'entity': entity,
                    'customer': inv_data['customer'],
                    'order_date': order_date.date(),
                    'required_date': (order_date + timedelta(days=30)).date(),
                    'ship_date': order_date.date(),
                    'delivery_date': order_date.date(),
                    'status': 'INVOICED',
                    'payment_status': 'PARTIAL' if inv_data['status'] in ['PARTIAL', 'ISSUED'] else inv_data['status'],
                    'subtotal': inv_data['subtotal'],
                    'tax_amount': tax_amount,
                    'shipping_cost': Decimal('0.00'),
                    'total_amount': total_amount,
                    'notes': f'Sample sales order {idx}',
                }
            )
            sample_orders.append(sales_order)

        # Create invoices
        created_invoices = []
        for idx, inv_data in enumerate(invoice_data, 1):
            invoice_date = timezone.now() - timedelta(days=inv_data['days_ago'])
            
            tax_amount = (inv_data['subtotal'] * inv_data['tax_percent']) / 100
            total_amount = inv_data['subtotal'] + tax_amount

            invoice, created = Invoice.objects.update_or_create(
                invoice_number=f'INV-2025-{100 + idx:03d}',
                defaults={
                    'customer': inv_data['customer'],
                    'entity': entity,
                    'sales_order': sample_orders[idx - 1],
                    'invoice_date': invoice_date.date(),
                    'due_date': (invoice_date + timedelta(days=30)).date(),
                    'subtotal': inv_data['subtotal'],
                    'tax_amount': tax_amount,
                    'total_amount': total_amount,
                    'amount_paid': inv_data['amount_paid'],
                    'status': inv_data['status'],
                    'notes': f'Sample invoice {idx} for testing P&L',
                }
            )
            created_invoices.append(invoice)
            status_txt = "Created" if created else "Updated"
            self.stdout.write(
                self.style.SUCCESS(
                    f'  [OK] {status_txt}: {invoice.invoice_number} - '
                    f'{inv_data["customer"].customer_name} - '
                    f'${invoice.total_amount:.2f} (Paid: ${invoice.amount_paid:.2f})'
                )
            )

        # Summary statistics
        total_invoices = len(created_invoices)
        total_subtotal = sum(inv.subtotal for inv in created_invoices)
        total_tax = sum(inv.tax_amount for inv in created_invoices)
        total_revenue = sum(inv.total_amount for inv in created_invoices)
        total_paid = sum(inv.amount_paid for inv in created_invoices)
        total_outstanding = total_revenue - total_paid

        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('SAMPLE DATA POPULATION SUMMARY'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f'[OK] Customers Created: {len(customers)}')
        self.stdout.write(f'[OK] Invoices Created: {total_invoices}')
        self.stdout.write(f'\nFINANCIAL SUMMARY:')
        self.stdout.write(f'  Total Subtotal:    ${total_subtotal:,.2f}')
        self.stdout.write(f'  Total Tax:         ${total_tax:,.2f}')
        self.stdout.write(f'  Total Revenue:     ${total_revenue:,.2f}')
        self.stdout.write(f'  Total Paid:        ${total_paid:,.2f}')
        self.stdout.write(f'  Outstanding AR:    ${total_outstanding:,.2f}')
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS('\nSample data population complete!'))
        self.stdout.write(self.style.SUCCESS(f'\nNext Steps:'))
        self.stdout.write(self.style.SUCCESS(f'  1. Login to ERP system'))
        self.stdout.write(self.style.SUCCESS(f'  2. Navigate to Accounting > P&L Detail'))
        self.stdout.write(self.style.SUCCESS(f'  3. View Revenue: ${total_subtotal:,.2f}'))
        self.stdout.write(self.style.SUCCESS(f'  4. Check GL entries in Accounting > Ledger'))
        self.stdout.write(self.style.SUCCESS(f'  5. Verify AR balance: ${total_outstanding:,.2f}'))
