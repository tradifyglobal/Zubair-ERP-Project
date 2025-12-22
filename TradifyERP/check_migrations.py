"""
Check and report migration status
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from django.db import connection

# Query applied migrations
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT name 
        FROM django_migrations 
        WHERE app = 'accounting' 
        ORDER BY id DESC 
        LIMIT 20
    """)
    migrations = cursor.fetchall()
    
    print("Last 20 applied migrations:")
    print("=" * 60)
    for i, (name,) in enumerate(migrations, 1):
        print(f"{i}. {name}")
