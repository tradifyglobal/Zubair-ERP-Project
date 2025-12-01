"""
Quick script to set is_staff=True for all users to enable admin access.
Run this with: python manage.py shell < fix_user_staff_status.py
Or manually in Django shell.
"""

from django.contrib.auth import get_user_model

User = get_user_model()

# Update all users to have staff status
updated_count = User.objects.filter(is_staff=False, is_superuser=False).update(is_staff=True)

print(f"✓ Updated {updated_count} users to have staff status")
print(f"Total users with staff access: {User.objects.filter(is_staff=True).count()}")
print(f"Total superusers: {User.objects.filter(is_superuser=True).count()}")
