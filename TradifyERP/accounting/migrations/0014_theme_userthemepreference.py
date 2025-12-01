"""
Migration to create Theme and UserThemePreference models.
This allows users to switch between themes while keeping all modules functional.
"""

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounting', '0001_initial'),  # Adjust this to match your latest migration
    ]

    operations = [
        migrations.CreateModel(
            name='Theme',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(
                    choices=[('minia', 'Minia - Dark Professional'), ('starterkit', 'Starter Kit - Light Clean')],
                    help_text='Unique identifier for the theme',
                    max_length=50,
                    unique=True
                )),
                ('display_name', models.CharField(help_text='Display name shown to users', max_length=100)),
                ('description', models.TextField(blank=True, help_text='Description of the theme')),
                ('is_active', models.BooleanField(default=True, help_text='Whether theme is available for selection')),
                ('thumbnail_url', models.CharField(
                    blank=True,
                    help_text='URL to theme thumbnail image',
                    max_length=500,
                    null=True
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Theme',
                'verbose_name_plural': 'Themes',
                'db_table': 'theme',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='UserThemePreference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sidebar_color', models.CharField(
                    choices=[('light', 'Light Sidebar'), ('dark', 'Dark Sidebar')],
                    default='light',
                    help_text='Sidebar color preference',
                    max_length=50
                )),
                ('layout_mode', models.CharField(
                    choices=[('vertical', 'Vertical Layout'), ('horizontal', 'Horizontal Layout')],
                    default='vertical',
                    help_text='Page layout mode',
                    max_length=50
                )),
                ('layout_size', models.CharField(
                    choices=[('fluid', 'Fluid Width'), ('boxed', 'Boxed Width')],
                    default='fluid',
                    help_text='Container width mode',
                    max_length=50
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('theme', models.ForeignKey(
                    default='minia',
                    help_text='Currently selected theme',
                    on_delete=django.db.models.deletion.PROTECT,
                    to='accounting.theme'
                )),
                ('user', models.OneToOneField(
                    help_text='User who has this preference',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='theme_preference',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'verbose_name': 'User Theme Preference',
                'verbose_name_plural': 'User Theme Preferences',
                'db_table': 'user_theme_preference',
            },
        ),
    ]
