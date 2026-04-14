# Generated migration for adding raw material support to PO

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('raw_materials', '0002_alter_rawmaterial_options_and_more'),
        ('procurement', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='polineitem',
            name='raw_material',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='po_line_items', to='raw_materials.rawmaterial'),
        ),
    ]
