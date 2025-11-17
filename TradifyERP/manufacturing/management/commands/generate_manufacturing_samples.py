"""
Management command to generate sample manufacturing data
Usage: python manage.py generate_manufacturing_samples --entity=1
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta

from manufacturing.models import (
    ProductCategory, Product, RawMaterial,
    BillOfMaterials, BOMLine,
    WorkCenter, Routing, RoutingLine,
    ProductionOrder
)
from accounting.models import Entity, Account


class Command(BaseCommand):
    help = 'Generate sample manufacturing data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--entity',
            type=int,
            default=1,
            help='Entity ID to create data for'
        )
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Delete existing sample data first'
        )

    def handle(self, *args, **options):
        entity_id = options['entity']
        delete_first = options['delete']

        try:
            entity = Entity.objects.get(id=entity_id)
        except Entity.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Entity {entity_id} not found'))
            return

        if delete_first:
            self.delete_sample_data(entity_id)

        self.stdout.write(self.style.SUCCESS(f'Creating sample data for {entity.name}...'))

        # Get GL accounts (or create simple ones)
        accounts = self.setup_accounts(entity)

        # Create categories
        categories = self.create_categories(entity, accounts)

        # Create raw materials
        materials = self.create_raw_materials(entity, accounts)

        # Create products
        products = self.create_products(entity, categories, accounts)

        # Create BOMs
        boms = self.create_boms(entity, products, materials)

        # Create work centers
        work_centers = self.create_work_centers(entity, accounts)

        # Create routings
        routings = self.create_routings(entity, products, work_centers)

        # Create production orders
        self.create_production_orders(entity, products, boms, routings)

        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))

    def setup_accounts(self, entity):
        """Get or create GL accounts for manufacturing."""
        accounts = {}
        account_types = {
            'Finished Goods Inventory': 'CURRENT_ASSET',
            'Raw Materials Inventory': 'CURRENT_ASSET',
            'Work in Process': 'CURRENT_ASSET',
            'Direct Labor': 'EXPENSE',
            'Manufacturing Overhead': 'EXPENSE',
        }

        for name, acct_type in account_types.items():
            acc, created = Account.objects.get_or_create(
                entity=entity,
                name=name,
                defaults={'account_type': acct_type}
            )
            accounts[name.lower().replace(' ', '_')] = acc

        return accounts

    def delete_sample_data(self, entity_id):
        """Delete existing sample data."""
        ProductionOrder.objects.filter(entity_id=entity_id).delete()
        Routing.objects.filter(entity_id=entity_id).delete()
        BOMLine.objects.filter(bom__entity_id=entity_id).delete()
        BillOfMaterials.objects.filter(entity_id=entity_id).delete()
        WorkCenter.objects.filter(entity_id=entity_id).delete()
        Product.objects.filter(entity_id=entity_id).delete()
        RawMaterial.objects.filter(entity_id=entity_id).delete()
        ProductCategory.objects.filter(entity_id=entity_id).delete()
        self.stdout.write(self.style.WARNING('Deleted existing sample data'))

    def create_categories(self, entity, accounts):
        """Create product categories."""
        categories = []
        category_data = [
            {'name': 'Electronics', 'code': 'ELEC'},
            {'name': 'Mechanical', 'code': 'MECH'},
            {'name': 'Assembly', 'code': 'ASSM'},
        ]

        for data in category_data:
            cat, created = ProductCategory.objects.get_or_create(
                entity=entity,
                code=data['code'],
                defaults={
                    'name': data['name'],
                    'revenue_account': accounts.get('finished_goods_inventory'),
                }
            )
            categories.append(cat)

        self.stdout.write(f'Created {len(categories)} categories')
        return categories

    def create_raw_materials(self, entity, accounts):
        """Create raw materials."""
        materials = []
        material_data = [
            {'code': 'MAT-001', 'name': 'Steel Sheet', 'cost': Decimal('25.00')},
            {'code': 'MAT-002', 'name': 'Aluminum Rod', 'cost': Decimal('15.50')},
            {'code': 'MAT-003', 'name': 'Plastic Resin', 'cost': Decimal('8.75')},
            {'code': 'MAT-004', 'name': 'Electronic Component', 'cost': Decimal('45.00')},
            {'code': 'MAT-005', 'name': 'Fastener Kit', 'cost': Decimal('3.50')},
        ]

        for data in material_data:
            mat, created = RawMaterial.objects.get_or_create(
                entity=entity,
                material_code=data['code'],
                defaults={
                    'name': data['name'],
                    'standard_unit_cost': data['cost'],
                    'reorder_quantity': Decimal('100'),
                    'reorder_point': Decimal('50'),
                    'current_stock': Decimal('200'),
                    'inventory_account': accounts.get('raw_materials_inventory'),
                }
            )
            materials.append(mat)

        self.stdout.write(f'Created {len(materials)} raw materials')
        return materials

    def create_products(self, entity, categories, accounts):
        """Create finished products."""
        products = []
        product_data = [
            {
                'code': 'PROD-001',
                'name': 'Industrial Widget',
                'cost': Decimal('150.00'),
                'price': Decimal('250.00'),
                'category': categories[0] if categories else None,
            },
            {
                'code': 'PROD-002',
                'name': 'Precision Assembly',
                'cost': Decimal('300.00'),
                'price': Decimal('500.00'),
                'category': categories[1] if len(categories) > 1 else None,
            },
            {
                'code': 'PROD-003',
                'name': 'Electronic Device',
                'cost': Decimal('200.00'),
                'price': Decimal('400.00'),
                'category': categories[0] if categories else None,
            },
        ]

        for data in product_data:
            prod, created = Product.objects.get_or_create(
                entity=entity,
                product_code=data['code'],
                defaults={
                    'name': data['name'],
                    'category': data['category'],
                    'standard_cost': data['cost'],
                    'selling_price': data['price'],
                    'is_manufactured': True,
                    'manufacturing_lead_time': 7,
                    'requires_inspection': True,
                    'inspection_level': 'BASIC',
                    'inventory_account': accounts.get('finished_goods_inventory'),
                }
            )
            products.append(prod)

        self.stdout.write(f'Created {len(products)} products')
        return products

    def create_boms(self, entity, products, materials):
        """Create bills of materials."""
        boms = []
        user = User.objects.first()

        for product in products[:2]:  # Create BOM for first 2 products
            bom, created = BillOfMaterials.objects.get_or_create(
                entity=entity,
                product=product,
                version=1,
                defaults={
                    'effective_date': date.today(),
                    'is_active': True,
                    'created_by': user,
                }
            )

            if created:
                # Add some bill of material lines
                for i, material in enumerate(materials[:3]):
                    BOMLine.objects.create(
                        bom=bom,
                        material=material,
                        quantity_per_unit=Decimal(2 + i),
                        scrap_percentage=Decimal('5'),
                        unit_cost=material.standard_unit_cost,
                        is_active=True,
                    )

            boms.append(bom)

        self.stdout.write(f'Created {len(boms)} BOMs')
        return boms

    def create_work_centers(self, entity, accounts):
        """Create work centers."""
        work_centers = []
        wc_data = [
            {
                'code': 'WC-001',
                'name': 'CNC Machining',
                'labor': Decimal('50.00'),
                'machine': Decimal('75.00'),
            },
            {
                'code': 'WC-002',
                'name': 'Assembly Line',
                'labor': Decimal('25.00'),
                'machine': Decimal('50.00'),
            },
            {
                'code': 'WC-003',
                'name': 'Quality Control',
                'labor': Decimal('30.00'),
                'machine': Decimal('10.00'),
            },
        ]

        for data in wc_data:
            wc, created = WorkCenter.objects.get_or_create(
                entity=entity,
                code=data['code'],
                defaults={
                    'name': data['name'],
                    'labor_cost_per_hour': data['labor'],
                    'machine_cost_per_hour': data['machine'],
                    'standard_hours_per_day': Decimal('8'),
                    'labor_expense_account': accounts.get('direct_labor'),
                    'machine_expense_account': accounts.get('manufacturing_overhead'),
                }
            )
            work_centers.append(wc)

        self.stdout.write(f'Created {len(work_centers)} work centers')
        return work_centers

    def create_routings(self, entity, products, work_centers):
        """Create routings."""
        routings = []
        user = User.objects.first()

        for product in products[:2]:
            routing, created = Routing.objects.get_or_create(
                entity=entity,
                product=product,
                version=1,
                defaults={
                    'effective_date': date.today(),
                    'is_active': True,
                    'created_by': user,
                }
            )

            if created:
                # Add routing lines
                for i, wc in enumerate(work_centers[:2]):
                    RoutingLine.objects.create(
                        routing=routing,
                        work_center=wc,
                        sequence=i + 1,
                        estimated_hours=Decimal(2 + i),
                        setup_hours=Decimal('1'),
                        is_active=True,
                    )

            routings.append(routing)

        self.stdout.write(f'Created {len(routings)} routings')
        return routings

    def create_production_orders(self, entity, products, boms, routings):
        """Create production orders."""
        orders = []
        user = User.objects.first()

        for i, product in enumerate(products[:2]):
            po_num = f'PO-{date.today().strftime("%Y%m%d")}-{i+1:03d}'
            order, created = ProductionOrder.objects.get_or_create(
                entity=entity,
                po_number=po_num,
                defaults={
                    'product': product,
                    'quantity_ordered': Decimal('100'),
                    'start_date': date.today(),
                    'due_date': date.today() + timedelta(days=7),
                    'status': 'PLANNED',
                    'bom': boms[i] if i < len(boms) else None,
                    'routing': routings[i] if i < len(routings) else None,
                    'created_by': user,
                }
            )
            orders.append(order)

        self.stdout.write(f'Created {len(orders)} production orders')
        return orders
