#!/usr/bin/env python
"""
Script to validate the current database schema and report what changes
are needed based on the desired cleanup.
"""
import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import inspect, text
from tabulate import tabulate

def validate_schema():
    """
    Validate the current database schema against the expected cleanup changes.
    Returns a report of what has already been changed and what still needs to be changed.
    """
    print("Validating database schema...")
    
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    # Tables to check if they should be dropped
    tables_to_check = ['sensor_data', 'wallet_transactions', 'wallets', 'reviews', 'payments']
    
    # Columns to check in parking_locations
    parking_location_cols = [
        'has_covered_parking',
        'has_ev_charging',
        'has_disabled_access',
        'has_cctv',
        'has_security',
        'rating'
    ]
    
    # Columns to check in parking_slots
    parking_slot_cols = [
        'level',
        'slot_type',
        'slot_size',
        'sensor_id'
    ]
    
    # Columns to check in vehicles
    vehicle_cols = [
        'make',
        'model'
    ]
    
    # Check tables
    tables_status = []
    for table in tables_to_check:
        exists = table in tables
        tables_status.append([table, "✅ Already dropped" if not exists else "❌ Still exists"])
    
    # Check columns in parking_locations
    parking_location_cols_status = []
    if 'parking_locations' in tables:
        columns = [col['name'] for col in inspector.get_columns('parking_locations')]
        for col in parking_location_cols:
            exists = col in columns
            parking_location_cols_status.append(['parking_locations.' + col, "✅ Already dropped" if not exists else "❌ Still exists"])
    
    # Check columns in parking_slots
    parking_slot_cols_status = []
    if 'parking_slots' in tables:
        columns = [col['name'] for col in inspector.get_columns('parking_slots')]
        for col in parking_slot_cols:
            exists = col in columns
            parking_slot_cols_status.append(['parking_slots.' + col, "✅ Already dropped" if not exists else "❌ Still exists"])
    
    # Check columns in vehicles
    vehicle_cols_status = []
    if 'vehicles' in tables:
        columns = [col['name'] for col in inspector.get_columns('vehicles')]
        for col in vehicle_cols:
            exists = col in columns
            vehicle_cols_status.append(['vehicles.' + col, "✅ Already dropped" if not exists else "❌ Still exists"])
    
    # Check payment_id in bookings
    bookings_cols_status = []
    if 'bookings' in tables:
        columns = [col['name'] for col in inspector.get_columns('bookings')]
        exists = 'payment_id' in columns
        bookings_cols_status.append(['bookings.payment_id', "✅ Already dropped" if not exists else "❌ Still exists"])
    
    # Print status reports
    print("\nDatabase Tables Status:")
    print(tabulate(tables_status, headers=["Table", "Status"], tablefmt="grid"))
    
    print("\nParking Locations Columns Status:")
    print(tabulate(parking_location_cols_status, headers=["Column", "Status"], tablefmt="grid"))
    
    print("\nParking Slots Columns Status:")
    print(tabulate(parking_slot_cols_status, headers=["Column", "Status"], tablefmt="grid"))
    
    print("\nVehicles Columns Status:")
    print(tabulate(vehicle_cols_status, headers=["Column", "Status"], tablefmt="grid"))
    
    print("\nBookings Columns Status:")
    print(tabulate(bookings_cols_status, headers=["Column", "Status"], tablefmt="grid"))
    
    # Check for parking locations
    locations = ['Alpha One Mall Parking', 'Himalaya Mall Parking', 'City Gold Multiplex Parking',
                'Central Mall Parking', 'Sabarmati Riverfront Parking', 'ISCON Mall Parking']
    
    # Execute SQL to check these locations
    conn = db.engine.connect()
    
    location_status = []
    for loc_name in locations:
        result = conn.execute(text(f"SELECT id, total_slots, available_slots FROM parking_locations "
                               f"WHERE name = '{loc_name}'"))
        row = result.fetchone()
        if row:
            id, total_slots, available_slots = row
            if total_slots >= 80 and total_slots <= 200 and available_slots == total_slots:
                status = "✅ Properly configured"
            else:
                status = f"⚠️ Found but needs update (slots: {total_slots}/{available_slots})"
        else:
            status = "❌ Not found"
        
        location_status.append([loc_name, status])
    
    print("\nDemo Parking Locations Status:")
    print(tabulate(location_status, headers=["Location", "Status"], tablefmt="grid"))
    
    conn.close()

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        validate_schema() 