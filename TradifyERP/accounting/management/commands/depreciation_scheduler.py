"""
Automated Depreciation Scheduler
Runs depreciation generation on a schedule without external dependencies.

Usage:
    python manage.py depreciation_scheduler --start
    python manage.py depreciation_scheduler --stop
    python manage.py depreciation_scheduler --status
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.utils import timezone
from datetime import datetime, timedelta
import time
import threading
import os
import json


class DepreciationScheduler:
    """Simple in-process scheduler for depreciation generation."""
    
    def __init__(self):
        self.config_file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'depreciation_scheduler.json')
        self.scheduler_thread = None
        self.is_running = False
        self.load_config()
    
    def load_config(self):
        """Load scheduler configuration."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                    self.is_running = self.config.get('is_running', False)
            except:
                self.config = self.get_default_config()
        else:
            self.config = self.get_default_config()
    
    def get_default_config(self):
        """Get default configuration."""
        return {
            'is_running': False,
            'run_time': '02:00',  # 2 AM daily
            'last_run': None,
            'next_run': None,
            'enabled': True,
            'created_at': datetime.now().isoformat()
        }
    
    def save_config(self):
        """Save scheduler configuration."""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2, default=str)
    
    def calculate_next_run(self):
        """Calculate next run time."""
        now = timezone.now()
        run_hour, run_minute = map(int, self.config['run_time'].split(':'))
        
        # Next run is tomorrow at run_time
        next_run = now.replace(hour=run_hour, minute=run_minute, second=0, microsecond=0)
        
        # If run time has passed today, use tomorrow
        if next_run <= now:
            next_run = next_run + timedelta(days=1)
        
        return next_run
    
    def should_run(self):
        """Check if scheduler should run now."""
        if not self.config['enabled']:
            return False
        
        now = timezone.now()
        run_hour, run_minute = map(int, self.config['run_time'].split(':'))
        
        # Check if current time matches run time (within 1 minute window)
        return (now.hour == run_hour and 
                now.minute == run_minute)
    
    def run_depreciation(self):
        """Run the depreciation generation."""
        try:
            from django.core.management import call_command
            call_command('generate_depreciation')
            self.config['last_run'] = datetime.now().isoformat()
            self.config['next_run'] = self.calculate_next_run().isoformat()
            self.save_config()
            return True, "Depreciation generated successfully"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def start(self):
        """Start the scheduler thread."""
        if self.is_running:
            return False, "Scheduler is already running"
        
        self.is_running = True
        self.config['is_running'] = True
        self.config['next_run'] = self.calculate_next_run().isoformat()
        self.save_config()
        
        def scheduler_loop():
            """Main scheduler loop running in background thread."""
            last_run_date = None
            
            while self.is_running:
                try:
                    # Check if we should run
                    now = timezone.now()
                    current_date = now.date()
                    
                    # Run once per day at specified time
                    if (self.should_run() and 
                        (last_run_date is None or last_run_date < current_date)):
                        
                        success, message = self.run_depreciation()
                        last_run_date = current_date
                        
                        log_msg = f"[{now.isoformat()}] {'✅' if success else '❌'} {message}"
                        self.log(log_msg)
                    
                    # Check every 30 seconds
                    time.sleep(30)
                
                except Exception as e:
                    self.log(f"[{timezone.now().isoformat()}] ❌ Scheduler error: {str(e)}")
                    time.sleep(60)  # Wait longer on error
        
        self.scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        return True, "Depreciation scheduler started successfully"
    
    def stop(self):
        """Stop the scheduler thread."""
        if not self.is_running:
            return False, "Scheduler is not running"
        
        self.is_running = False
        self.config['is_running'] = False
        self.save_config()
        
        # Wait for thread to stop
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        
        return True, "Depreciation scheduler stopped successfully"
    
    def get_status(self):
        """Get scheduler status."""
        return {
            'is_running': self.is_running,
            'enabled': self.config['enabled'],
            'run_time': self.config['run_time'],
            'last_run': self.config.get('last_run'),
            'next_run': self.config.get('next_run'),
            'created_at': self.config.get('created_at')
        }
    
    def log(self, message):
        """Log scheduler events."""
        log_file = os.path.join(os.path.dirname(self.config_file), 'depreciation_scheduler.log')
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, 'a') as f:
            f.write(message + '\n')


# Global scheduler instance
_scheduler = None


def get_scheduler():
    """Get or create the global scheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = DepreciationScheduler()
    return _scheduler


class Command(BaseCommand):
    help = 'Manage automated depreciation generation scheduler'

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            '--start',
            action='store_true',
            help='Start the depreciation scheduler'
        )
        group.add_argument(
            '--stop',
            action='store_true',
            help='Stop the depreciation scheduler'
        )
        group.add_argument(
            '--status',
            action='store_true',
            help='Show scheduler status'
        )
        group.add_argument(
            '--run-now',
            action='store_true',
            help='Run depreciation immediately'
        )
        
        parser.add_argument(
            '--time',
            type=str,
            help='Set run time in HH:MM format (e.g., 02:00)'
        )
        
        parser.add_argument(
            '--disable',
            action='store_true',
            help='Disable scheduler (won\'t run, but keeps config)'
        )
        
        parser.add_argument(
            '--enable',
            action='store_true',
            help='Enable scheduler'
        )

    def handle(self, *args, **options):
        scheduler = get_scheduler()
        
        if options['start']:
            success, message = scheduler.start()
            if success:
                self.stdout.write(self.style.SUCCESS(f"[OK] {message}"))
                status = scheduler.get_status()
                self.stdout.write(f"\n[SCHEDULED TIME] {status['run_time']}")
                self.stdout.write(f"[NEXT RUN] {status['next_run']}\n")
            else:
                self.stdout.write(self.style.ERROR(f"[ERROR] {message}"))
        
        elif options['stop']:
            success, message = scheduler.stop()
            if success:
                self.stdout.write(self.style.SUCCESS(f"[OK] {message}"))
            else:
                self.stdout.write(self.style.ERROR(f"[ERROR] {message}"))
        
        elif options['status']:
            status = scheduler.get_status()
            self.stdout.write("\n" + "="*60)
            self.stdout.write("DEPRECIATION SCHEDULER STATUS")
            self.stdout.write("="*60)
            self.stdout.write(f"\n[RUNNING] {'YES' if status['is_running'] else 'NO'}")
            self.stdout.write(f"[ENABLED] {'YES' if status['enabled'] else 'NO'}")
            self.stdout.write(f"[SCHEDULED TIME] {status['run_time']} daily")
            self.stdout.write(f"[NEXT RUN] {status['next_run'] or 'N/A'}")
            self.stdout.write(f"[LAST RUN] {status['last_run'] or 'Never'}")
            self.stdout.write(f"[CREATED] {status['created_at']}")
            self.stdout.write("\n" + "="*60 + "\n")
            
            # Show log tail
            log_file = os.path.join(os.path.dirname(scheduler.config_file), 'depreciation_scheduler.log')
            if os.path.exists(log_file):
                self.stdout.write("[RECENT LOGS]:\n")
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    for line in lines[-10:]:  # Last 10 lines
                        self.stdout.write(line.rstrip())
                self.stdout.write("\n")
        
        elif options['run_now']:
            self.stdout.write("[RUNNING] depreciation now...\n")
            success, message = scheduler.run_depreciation()
            if success:
                self.stdout.write(self.style.SUCCESS(f"[OK] {message}"))
            else:
                self.stdout.write(self.style.ERROR(f"[ERROR] {message}"))
        
        elif options['time']:
            # Validate time format
            try:
                hour, minute = map(int, options['time'].split(':'))
                if not (0 <= hour <= 23 and 0 <= minute <= 59):
                    raise ValueError("Invalid time values")
                scheduler.config['run_time'] = options['time']
                scheduler.save_config()
                self.stdout.write(self.style.SUCCESS(f"[OK] Scheduled time updated to {options['time']}"))
            except:
                self.stdout.write(self.style.ERROR("[ERROR] Invalid time format. Use HH:MM (e.g., 02:00)"))
        
        elif options['disable']:
            scheduler.config['enabled'] = False
            scheduler.save_config()
            self.stdout.write(self.style.WARNING("[WARNING] Scheduler disabled"))
        
        elif options['enable']:
            scheduler.config['enabled'] = True
            scheduler.save_config()
            self.stdout.write(self.style.SUCCESS("[OK] Scheduler enabled"))
