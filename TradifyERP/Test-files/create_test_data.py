#!/usr/bin/env python
"""Create test data for CRM module."""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from crm.models import CustomerGroup, Prospect, LeadSource, Territory, Contact, SalesPerson
from accounting.models import Entity
from django.contrib.auth.models import User

# Get or create entity
entity, created = Entity.objects.get_or_create(id=1, defaults={'name': 'Main Entity', 'code': 'MAIN'})
print(f"Entity: {entity.name} (ID: {entity.id})\n")

# Create test data
print("Creating test data...\n")

# 1. Territory
if Territory.objects.filter(entity=entity).count() == 0:
    territory = Territory.objects.create(
        entity=entity,
        territory_name="North America",
        region="NA",
        annual_target=100000
    )
    print(f"✓ Created Territory: {territory.territory_name}")

# 2. Customer Groups
if CustomerGroup.objects.filter(entity=entity).count() == 0:
    cg1 = CustomerGroup.objects.create(
        entity=entity,
        group_name="Enterprise",
        group_code="ENT001",
        description="Enterprise customers",
        is_active=True
    )
    cg2 = CustomerGroup.objects.create(
        entity=entity,
        group_name="SMB",
        group_code="SMB001",
        description="Small and Medium Business",
        is_active=True
    )
    print(f"✓ Created Customer Groups: {cg1.group_name}, {cg2.group_name}")

# 3. Lead Sources
if LeadSource.objects.filter(entity=entity).count() == 0:
    ls1 = LeadSource.objects.create(
        entity=entity,
        source_name="Website",
        source_code="WEB001",
        description="Leads from website",
        is_active=True
    )
    ls2 = LeadSource.objects.create(
        entity=entity,
        source_name="Referral",
        source_code="REF001",
        description="Referral leads",
        is_active=True
    )
    print(f"✓ Created Lead Sources: {ls1.source_name}, {ls2.source_name}")

# 4. Contacts
if Contact.objects.filter(entity=entity).count() == 0:
    contact = Contact.objects.create(
        entity=entity,
        contact_name="John Smith",
        email="john@example.com",
        phone="555-1234",
        company="ACME Corp",
        designation="Sales Manager"
    )
    print(f"✓ Created Contact: {contact.contact_name}")

# 5. Prospects
if Prospect.objects.filter(entity=entity).count() == 0:
    prospect = Prospect.objects.create(
        entity=entity,
        prospect_name="Tech Solutions Inc",
        company="Tech Solutions Inc",
        email="contact@techsol.com",
        phone="555-5678",
        status="NEW",
        probability=50,
        estimated_value=50000
    )
    print(f"✓ Created Prospect: {prospect.prospect_name}")

# 6. Sales Person
if SalesPerson.objects.filter(entity=entity).count() == 0:
    try:
        user = User.objects.first()  # Get first user
        if user:
            salesperson = SalesPerson.objects.create(
                entity=entity,
                user=user,
                employee_id="SP001",
                territory=Territory.objects.filter(entity=entity).first(),
                monthly_target=5000,
                annual_target=60000
            )
            print(f"✓ Created Sales Person: {salesperson.user.username}")
    except Exception as e:
        print(f"⚠ Could not create Sales Person: {e}")

print("\n===== TEST DATA SUMMARY =====")
print(f"Customer Groups: {CustomerGroup.objects.filter(entity=entity).count()}")
print(f"Lead Sources: {LeadSource.objects.filter(entity=entity).count()}")
print(f"Contacts: {Contact.objects.filter(entity=entity).count()}")
print(f"Prospects: {Prospect.objects.filter(entity=entity).count()}")
print(f"Territories: {Territory.objects.filter(entity=entity).count()}")
print(f"Sales Persons: {SalesPerson.objects.filter(entity=entity).count()}")
print("\n✓ Test data creation complete!")
