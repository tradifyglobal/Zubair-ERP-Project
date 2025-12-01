# Generated migration for Lead source field change
# This migration converts Lead.source from CharField with choices to ForeignKey to LeadSource

from django.db import migrations, models
import django.db.models.deletion


def create_default_lead_sources(apps, schema_editor):
    """Create default LeadSource records from the old choices."""
    LeadSource = apps.get_model('crm', 'LeadSource')
    Entity = apps.get_model('accounting', 'Entity')
    
    # Get or create the main entity
    entity, _ = Entity.objects.get_or_create(
        id=1,
        defaults={'name': 'Main Entity', 'code': 'MAIN'}
    )
    
    # Define the source mappings from old choices
    sources = [
        ('WEBSITE', 'Website', 'WEB'),
        ('REFERRAL', 'Referral', 'REF'),
        ('COLD_CALL', 'Cold Call', 'CALL'),
        ('EMAIL', 'Email Campaign', 'EMAIL'),
        ('TRADE_SHOW', 'Trade Show', 'SHOW'),
        ('SOCIAL_MEDIA', 'Social Media', 'SOCIAL'),
        ('ADVERTISEMENT', 'Advertisement', 'ADV'),
        ('INBOUND', 'Inbound Inquiry', 'INBOUND'),
        ('OTHER', 'Other', 'OTHER'),
    ]
    
    for code, name, short_code in sources:
        LeadSource.objects.get_or_create(
            entity=entity,
            source_code=short_code,
            defaults={
                'source_name': name,
                'description': f'Auto-created from legacy {code} source',
                'is_active': True
            }
        )


def migrate_lead_sources_data(apps, schema_editor):
    """Migrate existing Lead records to use LeadSource ForeignKey."""
    Lead = apps.get_model('crm', 'Lead')
    LeadSource = apps.get_model('crm', 'LeadSource')
    Entity = apps.get_model('accounting', 'Entity')
    
    entity = Entity.objects.get(id=1)
    
    # Mapping of old source choices to source codes
    source_mapping = {
        'WEBSITE': 'WEB',
        'REFERRAL': 'REF',
        'COLD_CALL': 'CALL',
        'EMAIL': 'EMAIL',
        'TRADE_SHOW': 'SHOW',
        'SOCIAL_MEDIA': 'SOCIAL',
        'ADVERTISEMENT': 'ADV',
        'INBOUND': 'INBOUND',
        'OTHER': 'OTHER',
    }
    
    for lead in Lead.objects.all():
        if lead.source in source_mapping:
            source_code = source_mapping[lead.source]
            try:
                lead_source = LeadSource.objects.get(entity=entity, source_code=source_code)
                lead.source_fk = lead_source
                lead.save(update_fields=['source_fk'])
            except LeadSource.DoesNotExist:
                # If source not found, leave as NULL
                pass


def reverse_migrate(apps, schema_editor):
    """Reverse migration - not implemented as it would require complex data conversion."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0003_add_new_crm_models'),
    ]

    operations = [
        # First add a new field to hold the FK
        migrations.AddField(
            model_name='lead',
            name='source_fk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='leads_temp', to='crm.leadsource'),
        ),
        # Create default lead sources
        migrations.RunPython(create_default_lead_sources),
        # Migrate data from CharField to FK
        migrations.RunPython(migrate_lead_sources_data, reverse_migrate),
        # Remove the old CharField field
        migrations.RemoveField(
            model_name='lead',
            name='source',
        ),
        # Rename the new FK field to source
        migrations.RenameField(
            model_name='lead',
            old_name='source_fk',
            new_name='source',
        ),
    ]
