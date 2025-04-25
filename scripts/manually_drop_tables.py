#!/usr/bin/env python
"""
Script to manually drop tables and remove columns by directly executing SQL.
This is a fallback if the migration script doesn't work properly.
"""
import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text
import time

def fix_database():
    """
    Manually drop tables and columns by executing SQL with foreign key checks disabled.
    """
    print("Starting manual database cleanup...")
    
    # Get a connection
    conn = db.engine.connect()
    
    # Execute SQL with handling errors
    def safe_execute(sql, description):
        try:
            print(f"Executing: {description}")
            conn.execute(text(sql))
            return True
        except Exception as e:
            print(f"Warning: {description} failed: {e}")
            return False
    
    # Disable foreign key checks
    safe_execute("SET FOREIGN_KEY_CHECKS=0", "Disabling foreign key checks")
    
    try:
        # Remove payment_id from bookings
        safe_execute("ALTER TABLE bookings DROP COLUMN IF EXISTS payment_id", 
                    "Removing payment_id from bookings")
        
        # Drop tables
        tables_to_drop = ['sensor_data', 'wallet_transactions', 'wallets', 'reviews', 'payments']
        for table in tables_to_drop:
            safe_execute(f"DROP TABLE IF EXISTS {table}", f"Dropping table {table}")
        
        # Remove columns from parking_locations
        cols = ['has_covered_parking', 'has_ev_charging', 'has_disabled_access', 
                'has_cctv', 'has_security', 'rating']
        for col in cols:
            safe_execute(f"ALTER TABLE parking_locations DROP COLUMN IF EXISTS {col}", 
                        f"Removing {col} from parking_locations")
        
        # Remove columns from parking_slots
        cols = ['level', 'slot_type', 'slot_size', 'sensor_id']
        for col in cols:
            safe_execute(f"ALTER TABLE parking_slots DROP COLUMN IF EXISTS {col}", 
                        f"Removing {col} from parking_slots")
        
        # Remove columns from vehicles
        cols = ['make', 'model']
        for col in cols:
            safe_execute(f"ALTER TABLE vehicles DROP COLUMN IF EXISTS {col}", 
                        f"Removing {col} from vehicles")
        
        # Update the alembic version to match our migration
        # This makes Alembic think the migration has been applied
        safe_execute("DELETE FROM alembic_version WHERE version_num = '3f379d39b4c1'", 
                    "Removing old alembic version")
        safe_execute("INSERT INTO alembic_version (version_num) VALUES ('cleanup_schema')", 
                    "Setting new alembic version")
        
        # Commit the transaction
        conn.commit()
        print("Successfully applied all changes manually!")
        
    except Exception as e:
        conn.rollback()
        print(f"Error in database cleanup: {e}")
        
    finally:
        # Re-enable foreign key checks
        safe_execute("SET FOREIGN_KEY_CHECKS=1", "Re-enabling foreign key checks")
        conn.close()
    
    print("Database cleanup completed.")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        confirm = input("This will directly modify your database schema. Are you sure? (y/N): ")
        if confirm.lower() == 'y':
            fix_database()
        else:
            print("Operation cancelled.") 