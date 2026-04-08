"""
Management command to load initial raw materials and related data
"""
from django.core.management.base import BaseCommand
from raw_materials.models import (
    RawMaterialCategory, Supplier, RawMaterial, Stock
)
from decimal import Decimal


class Command(BaseCommand):
    help = 'Load initial raw materials, categories, and suppliers'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n=== Loading Raw Materials Data ===\n'))

        # =====================================================================
        # 1. CREATE CATEGORIES
        # =====================================================================
        categories_data = [
            {'name': 'Polymer Base', 'description': 'Core polymer materials (PBAT, PLA)'},
            {'name': 'Fiber/Filler', 'description': 'Fiber and filler materials for composition'},
            {'name': 'Additive', 'description': 'Chemical additives and colorants'},
            {'name': 'Specialty', 'description': 'Specialty materials and intermediate products'},
            {'name': 'Packaging', 'description': 'Packaging materials and labels'},
        ]

        categories = {}
        for cat_data in categories_data:
            cat, created = RawMaterialCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description'], 'is_active': True}
            )
            categories[cat_data['name']] = cat
            status = 'Created' if created else 'Exists'
            self.stdout.write(f"  {status}: {cat.name}")

        self.stdout.write(self.style.SUCCESS(f'\n✓ Categories: {len(categories)} loaded\n'))

        # =====================================================================
        # 2. CREATE SUPPLIERS
        # =====================================================================
        suppliers_data = [
            {
                'code': 'SUP-001',
                'name': 'ABC Polymers',
                'email': 'sales@abcpolymers.com',
                'phone': '+91-9876543210',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'country': 'India',
                'payment_terms': 'NET30',
                'quality_rating': Decimal('4.5'),
            },
            {
                'code': 'SUP-002',
                'name': 'Natural Sources Ltd',
                'email': 'info@naturalsources.in',
                'phone': '+91-9876543211',
                'city': 'Mumbai',
                'state': 'Maharashtra',
                'country': 'India',
                'payment_terms': 'NET30',
                'quality_rating': Decimal('4.0'),
            },
            {
                'code': 'SUP-003',
                'name': 'Mineral Suppliers Inc',
                'email': 'sales@mineralsuppliers.com',
                'phone': '+91-9876543212',
                'city': 'Delhi',
                'state': 'Delhi',
                'country': 'India',
                'payment_terms': 'NET30',
                'quality_rating': Decimal('4.2'),
            },
            {
                'code': 'SUP-004',
                'name': 'Color Masters',
                'email': 'contact@colormasters.in',
                'phone': '+91-9876543213',
                'city': 'Pune',
                'state': 'Maharashtra',
                'country': 'India',
                'payment_terms': 'NET30',
                'quality_rating': Decimal('4.8'),
            },
            {
                'code': 'SUP-005',
                'name': 'Chemical House',
                'email': 'info@chemicalhouse.in',
                'phone': '+91-9876543214',
                'city': 'Hyderabad',
                'state': 'Telangana',
                'country': 'India',
                'payment_terms': 'NET60',
                'quality_rating': Decimal('4.1'),
            },
        ]

        suppliers = {}
        for sup_data in suppliers_data:
            code = sup_data.pop('code')
            sup, created = Supplier.objects.get_or_create(
                supplier_code=code,
                defaults={**sup_data, 'is_active': True}
            )
            suppliers[code] = sup
            status = 'Created' if created else 'Exists'
            self.stdout.write(f"  {status}: {sup.name}")

        self.stdout.write(self.style.SUCCESS(f'\n✓ Suppliers: {len(suppliers)} loaded\n'))

        # =====================================================================
        # 3. CREATE RAW MATERIALS & STOCK
        # =====================================================================
        materials_data = [
            {
                'code': 'RM-PBAT-001',
                'name': 'PBAT Granules',
                'category': 'Polymer Base',
                'unit': 'KG',
                'supplier': 'SUP-001',
                'price': Decimal('450.00'),
                'min_stock': Decimal('200'),
                'max_stock': Decimal('1000'),
                'reorder_qty': Decimal('500'),
                'current_stock': Decimal('800'),
            },
            {
                'code': 'RM-PLA-002',
                'name': 'PLA Granules',
                'category': 'Polymer Base',
                'unit': 'KG',
                'supplier': 'SUP-001',
                'price': Decimal('520.00'),
                'min_stock': Decimal('200'),
                'max_stock': Decimal('1000'),
                'reorder_qty': Decimal('500'),
                'current_stock': Decimal('750'),
            },
            {
                'code': 'RM-CS-003',
                'name': 'Corn Starch',
                'category': 'Fiber/Filler',
                'unit': 'KG',
                'supplier': 'SUP-002',
                'price': Decimal('280.00'),
                'min_stock': Decimal('150'),
                'max_stock': Decimal('500'),
                'reorder_qty': Decimal('250'),
                'current_stock': Decimal('350'),
            },
            {
                'code': 'RM-TPS-004',
                'name': 'Thermoplastic Starch',
                'category': 'Fiber/Filler',
                'unit': 'KG',
                'supplier': 'SUP-002',
                'price': Decimal('350.00'),
                'min_stock': Decimal('150'),
                'max_stock': Decimal('500'),
                'reorder_qty': Decimal('250'),
                'current_stock': Decimal('300'),
            },
            {
                'code': 'RM-CACO3-005',
                'name': 'Calcium Carbonate',
                'category': 'Additive',
                'unit': 'KG',
                'supplier': 'SUP-003',
                'price': Decimal('120.00'),
                'min_stock': Decimal('100'),
                'max_stock': Decimal('300'),
                'reorder_qty': Decimal('100'),
                'current_stock': Decimal('200'),
            },
            {
                'code': 'RM-MB-006',
                'name': 'Color Masterbatch',
                'category': 'Additive',
                'unit': 'KG',
                'supplier': 'SUP-004',
                'price': Decimal('650.00'),
                'min_stock': Decimal('50'),
                'max_stock': Decimal('200'),
                'reorder_qty': Decimal('75'),
                'current_stock': Decimal('120'),
            },
            {
                'code': 'RM-TIO2-007',
                'name': 'Titanium Dioxide',
                'category': 'Additive',
                'unit': 'KG',
                'supplier': 'SUP-003',
                'price': Decimal('890.00'),
                'min_stock': Decimal('25'),
                'max_stock': Decimal('100'),
                'reorder_qty': Decimal('50'),
                'current_stock': Decimal('60'),
            },
            {
                'code': 'RM-PLAST-008',
                'name': 'Glycerol Plasticizer',
                'category': 'Additive',
                'unit': 'KG',
                'supplier': 'SUP-005',
                'price': Decimal('410.00'),
                'min_stock': Decimal('50'),
                'max_stock': Decimal('200'),
                'reorder_qty': Decimal('100'),
                'current_stock': Decimal('150'),
            },
            {
                'code': 'RM-STAB-009',
                'name': 'Biodegradable Stabilizer',
                'category': 'Additive',
                'unit': 'KG',
                'supplier': 'SUP-005',
                'price': Decimal('550.00'),
                'min_stock': Decimal('50'),
                'max_stock': Decimal('150'),
                'reorder_qty': Decimal('75'),
                'current_stock': Decimal('100'),
            },
            {
                'code': 'RM-MESH-010',
                'name': 'Biodegradable Mesh Material',
                'category': 'Specialty',
                'unit': 'KG',
                'supplier': 'SUP-001',
                'price': Decimal('880.00'),
                'min_stock': Decimal('30'),
                'max_stock': Decimal('100'),
                'reorder_qty': Decimal('50'),
                'current_stock': Decimal('75'),
            },
            {
                'code': 'RM-NWF-011',
                'name': 'Non-woven PLA Fabric',
                'category': 'Specialty',
                'unit': 'KG',
                'supplier': 'SUP-002',
                'price': Decimal('720.00'),
                'min_stock': Decimal('25'),
                'max_stock': Decimal('100'),
                'reorder_qty': Decimal('50'),
                'current_stock': Decimal('80'),
            },
            {
                'code': 'RM-PLAFILM-012',
                'name': 'PLA Film Roll',
                'category': 'Specialty',
                'unit': 'KG',
                'supplier': 'SUP-001',
                'price': Decimal('680.00'),
                'min_stock': Decimal('20'),
                'max_stock': Decimal('80'),
                'reorder_qty': Decimal('40'),
                'current_stock': Decimal('65'),
            },
            {
                'code': 'RM-PACK-013',
                'name': 'Packaging Poly Roll',
                'category': 'Packaging',
                'unit': 'KG',
                'supplier': 'SUP-003',
                'price': Decimal('180.00'),
                'min_stock': Decimal('50'),
                'max_stock': Decimal('200'),
                'reorder_qty': Decimal('100'),
                'current_stock': Decimal('150'),
            },
            {
                'code': 'RM-LABEL-014',
                'name': 'Product Labels',
                'category': 'Packaging',
                'unit': 'PCS',
                'supplier': 'SUP-004',
                'price': Decimal('2.50'),
                'min_stock': Decimal('1000'),
                'max_stock': Decimal('5000'),
                'reorder_qty': Decimal('2000'),
                'current_stock': Decimal('3500'),
            },
            {
                'code': 'RM-CARTON-015',
                'name': 'Carton Boxes',
                'category': 'Packaging',
                'unit': 'PCS',
                'supplier': 'SUP-003',
                'price': Decimal('4.75'),
                'min_stock': Decimal('500'),
                'max_stock': Decimal('2000'),
                'reorder_qty': Decimal('1000'),
                'current_stock': Decimal('1500'),
            },
        ]

        materials_created = 0
        for mat_data in materials_data:
            code = mat_data.pop('code')
            name = mat_data.pop('name')
            category_name = mat_data.pop('category')
            unit = mat_data.pop('unit')
            supplier_code = mat_data.pop('supplier')
            price = mat_data.pop('price')
            min_stock = mat_data.pop('min_stock')
            max_stock = mat_data.pop('max_stock')
            reorder_qty = mat_data.pop('reorder_qty')
            current_stock = mat_data.pop('current_stock')

            # Create/get raw material
            mat, created = RawMaterial.objects.get_or_create(
                product_code=code,
                defaults={
                    'name': name,
                    'category': categories[category_name],
                    'unit_of_measure': unit,
                    'default_supplier': suppliers[supplier_code],
                    'current_unit_price': price,
                    'is_active': True,
                }
            )

            # Create/get stock record
            stock, stock_created = Stock.objects.get_or_create(
                raw_material=mat,
                defaults={
                    'quantity_on_hand': current_stock,
                    'minimum_stock_level': min_stock,
                    'maximum_stock_level': max_stock,
                    'reorder_quantity': reorder_qty,
                    'lead_time_days': 7,
                    'valuation_method': 'FIFO',
                    'standard_cost': price,
                }
            )

            if created:
                materials_created += 1
                self.stdout.write(f"  Created: {mat.product_code} - {mat.name}")

        self.stdout.write(self.style.SUCCESS(f'\n✓ Raw Materials: {materials_created} created\n'))

        # =====================================================================
        # 4. SUMMARY
        # =====================================================================
        total_materials = RawMaterial.objects.count()
        total_stock = Stock.objects.count()
        total_categories = RawMaterialCategory.objects.count()
        total_suppliers = Supplier.objects.count()

        self.stdout.write(self.style.SUCCESS('=== Data Load Complete ===\n'))
        self.stdout.write(f'Categories: {total_categories}')
        self.stdout.write(f'Suppliers: {total_suppliers}')
        self.stdout.write(f'Raw Materials: {total_materials}')
        self.stdout.write(f'Stock Records: {total_stock}')
        self.stdout.write(self.style.SUCCESS('\n✓ All raw materials data loaded successfully!\n'))
