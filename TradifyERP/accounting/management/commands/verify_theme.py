from django.core.management.base import BaseCommand
from accounting.models_theme import UserThemePreference, Theme
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Verify and test the theme switching system'

    def handle(self, *args, **options):
        try:
            user = User.objects.get(username='zubair')
            pref = UserThemePreference.objects.get(user=user)
            
            self.stdout.write(self.style.SUCCESS('✓ Current Theme Configuration:'))
            self.stdout.write(f'  Theme: {pref.theme.name}')
            self.stdout.write(f'  Sidebar: {pref.sidebar_color}')
            self.stdout.write(f'  Layout: {pref.layout_mode}')
            self.stdout.write(f'  Size: {pref.layout_size}')
            
            self.stdout.write('\n✓ Body tag should render as:')
            body_tag = f'<body data-bs-theme="{pref.sidebar_color}" data-sidebar="{pref.sidebar_color}" data-layout="{pref.layout_mode}" data-layout-size="{pref.layout_size}">'
            self.stdout.write(f'  {body_tag}')
            
            self.stdout.write('\n✓ CSS selectors that should apply:')
            self.stdout.write(f'  body[data-bs-theme="{pref.sidebar_color}"]')
            self.stdout.write(f'  body[data-sidebar="{pref.sidebar_color}"]')
            self.stdout.write(f'  body[data-layout="{pref.layout_mode}"]')
            self.stdout.write(f'  body[data-layout-size="{pref.layout_size}"]')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
