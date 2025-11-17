from django.core.management.base import BaseCommand
from inventory.models import Category, Product, Warehouse, Stock, StockMovement, PurchaseOrder, PurchaseOrderLine
from datetime import datetime


class Command(BaseCommand):
    help = 'Populate sample inventory data'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample inventory data...')

        # Create Categories
        categories = {}
        category_data = [
            {'name': 'Electronics', 'description': 'Electronic components and devices'},
            {'name': 'Raw Materials', 'description': 'Raw materials for manufacturing'},
            {'name': 'Finished Goods', 'description': 'Ready-to-sell products'},
            {'name': 'Office Supplies', 'description': 'Office and stationery supplies'},
        ]
        
        for cat_data in category_data:
            cat, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            categories[cat_data['name']] = cat
            if created:
                self.stdout.write(f"✓ Created category: {cat.name}")

        # Create Products
        products = {}
        product_data = [
            {
                'sku': 'ELEC-001',
                'name': 'Microcontroller Unit (MCU)',
                'category': 'Electronics',
                'cost_price': 15.00,
                'selling_price': 35.00,
                'reorder_level': 50,
                'reorder_quantity': 200,
            },
            {
                'sku': 'ELEC-002',
                'name': 'LED Display Module',
                'category': 'Electronics',
                'cost_price': 25.00,
                'selling_price': 65.00,
                'reorder_level': 30,
                'reorder_quantity': 100,
            },
            {
                'sku': 'RAW-001',
                'name': 'Copper Wire (per kg)',
                'category': 'Raw Materials',
                'cost_price': 8.50,
                'selling_price': 18.00,
                'reorder_level': 100,
                'reorder_quantity': 500,
            },
            {
                'sku': 'RAW-002',
                'name': 'Aluminum Sheet (per unit)',
                'category': 'Raw Materials',
                'cost_price': 12.00,
                'selling_price': 28.00,
                'reorder_level': 50,
                'reorder_quantity': 200,
            },
            {
                'sku': 'FG-001',
                'name': 'Smart Home Hub',
                'category': 'Finished Goods',
                'cost_price': 120.00,
                'selling_price': 299.99,
                'reorder_level': 10,
                'reorder_quantity': 50,
            },
            {
                'sku': 'FG-002',
                'name': 'IoT Temperature Sensor',
                'category': 'Finished Goods',
                'cost_price': 45.00,
                'selling_price': 129.99,
                'reorder_level': 20,
                'reorder_quantity': 100,
            },
            {
                'sku': 'OFFICE-001',
                'name': 'A4 Paper Ream (500 sheets)',
                'category': 'Office Supplies',
                'cost_price': 3.50,
                'selling_price': 8.99,
                'reorder_level': 100,
                'reorder_quantity': 500,
            },
        ]

        for prod_data in product_data:
            prod, created = Product.objects.get_or_create(
                sku=prod_data['sku'],
                defaults={
                    'name': prod_data['name'],
                    'category': categories[prod_data['category']],
                    'cost_price': prod_data['cost_price'],
                    'selling_price': prod_data['selling_price'],
                    'reorder_level': prod_data['reorder_level'],
                    'reorder_quantity': prod_data['reorder_quantity'],
                    'status': 'active',
                }
            )
            products[prod_data['sku']] = prod
            if created:
                self.stdout.write(f"✓ Created product: {prod.sku} - {prod.name}")

        # Create Warehouses
        warehouses = {}
        warehouse_data = [
            {
                'name': 'Main Warehouse',
                'location': 'Building A, Floor 1',
                'contact_person': 'John Smith',
                'phone': '+1-555-0001',
            },
            {
                'name': 'Secondary Warehouse',
                'location': 'Building B, Floor 2',
                'contact_person': 'Jane Doe',
                'phone': '+1-555-0002',
            },
            {
                'name': 'Distribution Center',
                'location': 'Industrial Park, Zone 3',
                'contact_person': 'Bob Johnson',
                'phone': '+1-555-0003',
            },
        ]

        for wh_data in warehouse_data:
            wh, created = Warehouse.objects.get_or_create(
                name=wh_data['name'],
                defaults={
                    'location': wh_data['location'],
                    'contact_person': wh_data['contact_person'],
                    'phone': wh_data['phone'],
                    'is_active': True,
                }
            )
            warehouses[wh_data['name']] = wh
            if created:
                self.stdout.write(f"✓ Created warehouse: {wh.name}")

        # Create Stock Records
        stock_data = [
            {'product': 'ELEC-001', 'warehouse': 'Main Warehouse', 'quantity': 250},
            {'product': 'ELEC-001', 'warehouse': 'Secondary Warehouse', 'quantity': 150},
            {'product': 'ELEC-002', 'warehouse': 'Main Warehouse', 'quantity': 80},
            {'product': 'ELEC-002', 'warehouse': 'Distribution Center', 'quantity': 120},
            {'product': 'RAW-001', 'warehouse': 'Main Warehouse', 'quantity': 500},
            {'product': 'RAW-002', 'warehouse': 'Main Warehouse', 'quantity': 200},
            {'product': 'FG-001', 'warehouse': 'Secondary Warehouse', 'quantity': 45},
            {'product': 'FG-002', 'warehouse': 'Distribution Center', 'quantity': 75},
            {'product': 'OFFICE-001', 'warehouse': 'Main Warehouse', 'quantity': 2000},
        ]

        for stock_item in stock_data:
            stock, created = Stock.objects.get_or_create(
                product=products[stock_item['product']],
                warehouse=warehouses[stock_item['warehouse']],
                defaults={'quantity_on_hand': stock_item['quantity']}
            )
            if created:
                self.stdout.write(
                    f"✓ Created stock: {stock_item['quantity']} units of "
                    f"{stock_item['product']} at {stock_item['warehouse']}"
                )

        # Create Stock Movements (Audit trail)
        movement_data = [
            {'product': 'ELEC-001', 'warehouse': 'Main Warehouse', 'type': 'in', 'qty': 200, 'ref': 'PO-2025-001'},
            {'product': 'ELEC-002', 'warehouse': 'Distribution Center', 'type': 'out', 'qty': 15, 'ref': 'SO-2025-042'},
            {'product': 'RAW-001', 'warehouse': 'Main Warehouse', 'type': 'in', 'qty': 300, 'ref': 'PO-2025-002'},
            {'product': 'FG-001', 'warehouse': 'Secondary Warehouse', 'type': 'out', 'qty': 5, 'ref': 'SO-2025-043'},
        ]

        for mov_data in movement_data:
            movement, created = StockMovement.objects.get_or_create(
                product=products[mov_data['product']],
                warehouse=warehouses[mov_data['warehouse']],
                reference_number=mov_data['ref'],
                defaults={
                    'movement_type': mov_data['type'],
                    'quantity': mov_data['qty'],
                    'created_by': 'admin',
                }
            )
            if created:
                self.stdout.write(
                    f"✓ Created movement: {mov_data['type'].upper()} "
                    f"{mov_data['qty']} units of {mov_data['product']}"
                )

        # Create Purchase Orders
        po_data = [
            {
                'po_number': 'PO-2025-001',
                'supplier': 'Electronics Supply Corp',
                'status': 'confirmed',
                'warehouse': 'Main Warehouse',
                'lines': [
                    {'product': 'ELEC-001', 'quantity': 200, 'unit_cost': 15.00},
                    {'product': 'ELEC-002', 'quantity': 100, 'unit_cost': 25.00},
                ]
            },
            {
                'po_number': 'PO-2025-002',
                'supplier': 'Raw Materials Ltd',
                'status': 'pending',
                'warehouse': 'Main Warehouse',
                'lines': [
                    {'product': 'RAW-001', 'quantity': 300, 'unit_cost': 8.50},
                    {'product': 'RAW-002', 'quantity': 150, 'unit_cost': 12.00},
                ]
            },
        ]

        for po_item in po_data:
            po, created = PurchaseOrder.objects.get_or_create(
                po_number=po_item['po_number'],
                defaults={
                    'supplier': po_item['supplier'],
                    'status': po_item['status'],
                    'warehouse': warehouses[po_item['warehouse']],
                }
            )
            
            if created:
                total = 0
                for line_data in po_item['lines']:
                    line, _ = PurchaseOrderLine.objects.get_or_create(
                        purchase_order=po,
                        product=products[line_data['product']],
                        defaults={
                            'quantity_ordered': line_data['quantity'],
                            'unit_cost': line_data['unit_cost'],
                        }
                    )
                    total += line.line_total
                
                po.total_amount = total
                po.save()
                self.stdout.write(f"✓ Created PO: {po.po_number} with total ${total:.2f}")

        self.stdout.write(self.style.SUCCESS('\n✅ Sample inventory data created successfully!'))
