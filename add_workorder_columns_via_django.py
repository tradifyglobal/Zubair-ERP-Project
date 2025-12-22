"""
Add missing columns to maintenance_work_order table using raw SQL via Django connection
"""
from django.db import connection

def add_columns():
    with connection.cursor() as cursor:
        try:
            # Add completion_date column
            cursor.execute("""
                ALTER TABLE maintenance_work_order 
                ADD COLUMN IF NOT EXISTS completion_date DATE NULL
            """)
            print("✓ Added completion_date column")
        except Exception as e:
            print(f"Error adding completion_date: {e}")
        
        try:
            # Add is_posted_to_gl column
            cursor.execute("""
                ALTER TABLE maintenance_work_order 
                ADD COLUMN IF NOT EXISTS is_posted_to_gl BOOLEAN DEFAULT FALSE NOT NULL
            """)
            print("✓ Added is_posted_to_gl column")
        except Exception as e:
            print(f"Error adding is_posted_to_gl: {e}")
    
    # Verify columns were added
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'maintenance_work_order'
            AND column_name IN ('completion_date', 'is_posted_to_gl')
            ORDER BY column_name
        """)
        
        results = cursor.fetchall()
        print("\nVerification:")
        for row in results:
            print(f"  {row[0]}: {row[1]} (nullable: {row[2]})")
        
        if len(results) == 2:
            print("\n✓ Both columns successfully added!")
            
            # Mark migration as applied
            cursor.execute("""
                INSERT INTO django_migrations (app, name, applied)
                VALUES ('maintenance', '0003_workorder_completion_date_workorder_is_posted_to_gl', NOW())
                ON CONFLICT DO NOTHING
            """)
            print("✓ Migration marked as applied")
        else:
            print(f"\n✗ Only {len(results)} column(s) found")

if __name__ == '__main__':
    add_columns()
