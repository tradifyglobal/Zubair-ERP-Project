#!/usr/bin/env python
"""
Script to delete specified users
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from django.contrib.auth.models import User

# Users to delete
users_to_delete = ['ahmed', 'test']

print("Users to delete:")
for username in users_to_delete:
    user = User.objects.filter(username=username).first()
    if user:
        print(f"  - {user.username} ({user.get_full_name()}) - {user.email}")
    else:
        print(f"  - {username} (NOT FOUND)")

print("\nDeleting users...")
deleted_count = 0
for username in users_to_delete:
    try:
        user = User.objects.get(username=username)
        email = user.email
        full_name = user.get_full_name()
        user.delete()
        deleted_count += 1
        print(f"  ✓ Deleted {username} ({full_name})")
    except User.DoesNotExist:
        print(f"  ✗ User '{username}' not found - skipping")
    except Exception as e:
        print(f"  ✗ Error deleting '{username}': {str(e)}")

print(f"\n✓ Successfully deleted {deleted_count} users")

# Verify deletion
print("\nVerification - Checking if users still exist:")
for username in users_to_delete:
    exists = User.objects.filter(username=username).exists()
    status = "EXISTS" if exists else "DELETED"
    print(f"  {username}: {status}")
