from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.test import Client

class Command(BaseCommand):
    help = 'Save dashboard HTML to file for inspection'

    def handle(self, *args, **options):
        try:
            user = User.objects.get(username='zubair')
            client = Client()
            client.force_login(user)
            
            response = client.get('/accounting/dashboard/')
            content = response.content.decode()
            
            # Save to file
            with open('dashboard_response.html', 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Print first 3000 chars to console
            self.stdout.write("First 3000 characters of HTML:")
            self.stdout.write("=" * 80)
            print(content[:3000])
            self.stdout.write("=" * 80)
            
            # Check for attributes
            self.stdout.write("\nSearching for theme attributes:")
            if 'data-bs-theme=' in content:
                self.stdout.write(self.style.SUCCESS('✓ Found data-bs-theme'))
            else:
                self.stdout.write(self.style.ERROR('✗ Missing data-bs-theme'))
                
            if 'data-sidebar=' in content:
                self.stdout.write(self.style.SUCCESS('✓ Found data-sidebar'))
            else:
                self.stdout.write(self.style.ERROR('✗ Missing data-sidebar'))
            
            self.stdout.write(f"\nTotal HTML size: {len(content)} bytes")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
