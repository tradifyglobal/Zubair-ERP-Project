from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Add missing columns to maintenance_work_order table'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            try:
                cursor.execute("""
                    ALTER TABLE maintenance_work_order 
                    ADD COLUMN IF NOT EXISTS completion_date DATE NULL
                """)
                self.stdout.write(self.style.SUCCESS('✓ Added completion_date column'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error adding completion_date: {e}'))
            
            try:
                cursor.execute("""
                    ALTER TABLE maintenance_work_order 
                    ADD COLUMN IF NOT EXISTS is_posted_to_gl BOOLEAN DEFAULT FALSE NOT NULL
                """)
                self.stdout.write(self.style.SUCCESS('✓ Added is_posted_to_gl column'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error adding is_posted_to_gl: {e}'))
        
        # Verify
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = 'maintenance_work_order'
                AND column_name IN ('completion_date', 'is_posted_to_gl')
            """)
            results = cursor.fetchall()
            
            self.stdout.write('\nVerification:')
            for row in results:
                self.stdout.write(f'  {row[0]}: {row[1]}')
            
            if len(results) == 2:
                # Mark migration as applied
                cursor.execute("""
                    INSERT INTO django_migrations (app, name, applied)
                    VALUES ('maintenance', '0003_workorder_completion_date_workorder_is_posted_to_gl', NOW())
                    ON CONFLICT DO NOTHING
                """)
                self.stdout.write(self.style.SUCCESS('\n✓ Migration marked as applied'))
