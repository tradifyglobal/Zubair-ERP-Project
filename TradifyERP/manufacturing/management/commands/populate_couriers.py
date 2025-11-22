"""
Management command to populate courier/carrier list.
"""

from django.core.management.base import BaseCommand
from manufacturing.models import Courier
from accounting.models import Entity


class Command(BaseCommand):
    help = 'Populate courier/carrier list'

    COURIERS = [
        ('DTDC', 'Dtdc', 'DTDC courier services'),
        ('DEL', 'Delhivery', 'Delhivery express delivery'),
        ('BA', 'Blue Dart', 'Blue Dart courier'),
        ('ECOM', 'Ecom Express', 'Ecom Express services'),
        ('FEDEX', 'FedEx', 'FedEx international courier'),
        ('GATI', 'Gati', 'Gati courier services'),
        ('DHL', 'Dhl', 'DHL courier services'),
        ('ARAMEX', 'Aramex', 'Aramex international courier'),
        ('XB', 'Xpressbees', 'Xpressbees delivery services'),
        ('IP', 'India Post', 'India Post services'),
        ('EKART', 'Ekart Logistics', 'Ekart Logistics'),
        ('SF', 'Shadowfax', 'Shadowfax logistics'),
        ('SAFE', 'Safexpress', 'Safexpress courier'),
        ('TPC', 'The Professional Couriers', 'The Professional Couriers'),
        ('UPS', 'Ups', 'UPS courier services'),
        ('MLL', 'Mahindra Logistics', 'Mahindra Logistics Limited'),
        ('NG', 'Nimbusglobal', 'Nimbusglobal logistics'),
        ('RIC', 'Reliable International courier services', 'Reliable International Courier Services'),
        ('AHU', 'Ahura Express', 'Ahura Express services'),
        ('BOM', 'Bombino', 'Bombino courier'),
        ('BUDCOUR', 'Budget Couriers Private Limited', 'Budget Couriers Private Limited'),
        ('DBS', 'DB Schenker', 'DB Schenker logistics'),
        ('FEI', 'FedEx Express India', 'FedEx Express India'),
        ('FFC', 'First Flight Couriers', 'First Flight Couriers'),
    ]

    def handle(self, *args, **options):
        # Get default entity (first one, or create if needed)
        try:
            entity = Entity.objects.first()
            if not entity:
                self.stdout.write(
                    self.style.ERROR('No Entity found. Please create an entity first.')
                )
                return
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error getting entity: {str(e)}')
            )
            return

        created_count = 0
        updated_count = 0

        for code, name, description in self.COURIERS:
            courier, created = Courier.objects.get_or_create(
                entity=entity,
                code=code,
                defaults={
                    'name': name,
                    'description': description,
                    'is_active': True,
                }
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created courier: {name}')
                )
            else:
                updated_count += 1
                # Update if needed
                if courier.name != name or courier.description != description:
                    courier.name = name
                    courier.description = description
                    courier.save()
                    self.stdout.write(
                        self.style.WARNING(f'✓ Updated courier: {name}')
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(f'→ Courier already exists: {name}')
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Completed! Created: {created_count}, Updated: {updated_count}'
            )
        )
