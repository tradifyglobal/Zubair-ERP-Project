"""
Auto-start depreciation scheduler on Django startup.

Add this to your wsgi.py or manage.py to auto-start the scheduler.
"""

import os
import django
from django.conf import settings

def start_depreciation_scheduler():
    """Initialize and start the depreciation scheduler."""
    try:
        # Only start if DEBUG is True or explicitly enabled
        if not settings.DEBUG:
            # Optional: Check for explicit setting
            if not getattr(settings, 'DEPRECATION_SCHEDULER_ENABLED', False):
                return
        
        from accounting.management.commands.depreciation_scheduler import get_scheduler
        
        scheduler = get_scheduler()
        
        # Load saved config
        scheduler.load_config()
        
        # Auto-start if it was previously running
        if scheduler.config.get('auto_start', True) and not scheduler.is_running:
            success, message = scheduler.start()
            if success:
                print(f"✅ {message}")
                print(f"   📅 Daily run scheduled at {scheduler.config['run_time']}")
            else:
                print(f"⚠️  {message}")
    except Exception as e:
        print(f"⚠️  Could not start depreciation scheduler: {str(e)}")


# Auto-start on import
start_depreciation_scheduler()
