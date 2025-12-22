#!/usr/bin/env python3
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from django.db import connection

print("Database Engine:", connection.settings_dict["ENGINE"])
print("Database Name:", connection.settings_dict["NAME"])  
print("Database Host:", connection.settings_dict.get("HOST", "localhost"))
print("Database Port:", connection.settings_dict.get("PORT", "5432"))

# Test the connection
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT version()")
        result = cursor.fetchone()
        print("PostgreSQL Version:", result[0])
    print("✅ Successfully connected to PostgreSQL!")
except Exception as e:
    print("❌ Database connection failed:", e)