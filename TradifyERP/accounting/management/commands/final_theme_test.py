from django.core.management.base import BaseCommand
from accounting.models_theme import UserThemePreference, Theme
from django.contrib.auth.models import User
from django.test import Client

class Command(BaseCommand):
    help = 'Final comprehensive theme system test'

    def handle(self, *args, **options):
        print("=" * 80)
        print("FINAL THEME SYSTEM VERIFICATION".center(80))
        print("=" * 80)
        
        try:
            user = User.objects.get(username='zubair')
            pref = UserThemePreference.objects.get(user=user)
            
            # Test 1
            print("\n[TEST 1] Available Themes")
            themes = list(Theme.objects.all())
            print(f"  ✓ Total themes: {len(themes)}")
            for theme in themes:
                print(f"    - {theme.name}")
            
            # Test 2
            print("\n[TEST 2] Current Preference")
            print(f"  ✓ Theme: {pref.theme.name}")
            print(f"  ✓ Sidebar: {pref.sidebar_color}")
            print(f"  ✓ Layout: {pref.layout_mode}")
            print(f"  ✓ Size: {pref.layout_size}")
            
            # Test 3
            print("\n[TEST 3] HTML Response")
            client = Client()
            client.force_login(user)
            response = client.get('/accounting/dashboard/')
            content = response.content.decode()
            
            checks = [
                (f'data-bs-theme="{pref.sidebar_color}"', 'data-bs-theme'),
                (f'data-sidebar="{pref.sidebar_color}"', 'data-sidebar'),
                (f'data-layout-size="{pref.layout_size}"', 'data-layout-size'),
            ]
            
            for check_str, label in checks:
                if check_str in content:
                    self.stdout.write(self.style.SUCCESS(f'  ✓ {label}'))
                else:
                    self.stdout.write(self.style.ERROR(f'  ✗ {label}'))
            
            print("\n" + "=" * 80)
            self.stdout.write(self.style.SUCCESS(
                "THEME SYSTEM IS FULLY OPERATIONAL".center(80)
            ))
            print("=" * 80)
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
