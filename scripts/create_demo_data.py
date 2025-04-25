"""
Script to populate the database with demo data for testing.
This script creates sample locations, slots, and other necessary data.
"""
import sys
import os
import random

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.parking_location import ParkingLocation
from app.models.parking_slot import ParkingSlot
from datetime import datetime
from sqlalchemy import text

def create_demo_data():
    """Create demo data for the application"""
    print("Creating demo data...")
    
    # Create sample parking locations
    locations = [
        {
            "name": "Alpha One Mall Parking",
            "address": "Vastrapur Lake, Ahmedabad",
            "area": "Vastrapur",
            "city": "Ahmedabad",
            "state": "Gujarat",
            "pincode": "380015",
            "latitude": 23.0469,
            "longitude": 72.5308,
            "total_slots": 120,
            "available_slots": 85,
            "hourly_rate": 30.0,
            "is_24_hours": True,
            "image_url": "/static/images/locations/mall-parking.jpg"
        },
        {
            "name": "Himalaya Mall Parking",
            "address": "Drive In Road, Gurukul",
            "area": "Gurukul",
            "city": "Ahmedabad",
            "state": "Gujarat",
            "pincode": "380052",
            "latitude": 23.0478,
            "longitude": 72.5438,
            "total_slots": 150,
            "available_slots": 62,
            "hourly_rate": 25.0,
            "is_24_hours": True,
            "image_url": "/static/images/locations/mall-parking.jpg"
        },
        {
            "name": "City Gold Multiplex Parking",
            "address": "Ashram Road, Ahmedabad",
            "area": "Ashram Road",
            "city": "Ahmedabad",
            "state": "Gujarat",
            "pincode": "380009",
            "latitude": 23.0383,
            "longitude": 72.5483,
            "total_slots": 80,
            "available_slots": 35,
            "hourly_rate": 20.0,
            "is_24_hours": True,
            "image_url": "/static/images/locations/multiplex-parking.jpg"
        },
        {
            "name": "Central Mall Parking",
            "address": "Ambawadi, Ahmedabad",
            "area": "Ambawadi",
            "city": "Ahmedabad",
            "state": "Gujarat",
            "pincode": "380015",
            "latitude": 23.0365,
            "longitude": 72.5559,
            "total_slots": 100,
            "available_slots": 48,
            "hourly_rate": 30.0,
            "is_24_hours": True,
            "image_url": "/static/images/locations/mall-parking.jpg"
        },
        {
            "name": "Sabarmati Riverfront Parking",
            "address": "Riverfront West, Usmanpura",
            "area": "Usmanpura",
            "city": "Ahmedabad",
            "state": "Gujarat",
            "pincode": "380013",
            "latitude": 23.0508,
            "longitude": 72.5757,
            "total_slots": 200,
            "available_slots": 180,
            "hourly_rate": 15.0,
            "is_24_hours": True,
            "image_url": "/static/images/locations/riverfront-parking.jpg"
        },
        {
            "name": "ISCON Mall Parking",
            "address": "SG Highway, Satellite",
            "area": "Satellite",
            "city": "Ahmedabad",
            "state": "Gujarat",
            "pincode": "380015",
            "latitude": 23.0301,
            "longitude": 72.5124,
            "total_slots": 130,
            "available_slots": 72,
            "hourly_rate": 25.0,
            "is_24_hours": True,
            "image_url": "/static/images/locations/mall-parking.jpg"
        }
    ]
    
    try:
        # Use raw SQL to disable foreign key checks and clear tables
        connection = db.engine.connect()
        
        # MySQL-specific: Disable foreign key checks temporarily
        connection.execute(text("SET FOREIGN_KEY_CHECKS=0"))
        
        # Clean existing data
        print("Cleaning existing data...")
        connection.execute(text("TRUNCATE TABLE parking_slots"))
        connection.execute(text("TRUNCATE TABLE parking_locations"))
        
        # Re-enable foreign key checks
        connection.execute(text("SET FOREIGN_KEY_CHECKS=1"))
        connection.close()
        
        # Create locations
        created_locations = []
        for location_data in locations:
            location = ParkingLocation(**location_data)
            db.session.add(location)
            db.session.flush()  # Get ID without committing
            created_locations.append(location)
            print(f"Created location: {location.name}")
        
        # Create parking slots for each location
        for location in created_locations:
            for i in range(1, location.total_slots + 1):
                slot_number = f"{location.area[:3].upper()}-{i:03d}"
                slot = ParkingSlot(
                    parking_location_id=location.id,
                    slot_number=slot_number,
                    vehicle_type="any",
                    is_active=True,
                    is_occupied=False,
                    hourly_rate=location.hourly_rate,
                    latitude=location.latitude + (random.random() * 0.0005),
                    longitude=location.longitude + (random.random() * 0.0005)
                )
                db.session.add(slot)
            print(f"Created {location.total_slots} slots for {location.name}")
        
        # Commit all changes
        db.session.commit()
        print("Demo data creation completed successfully!")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating demo data: {str(e)}")
        raise

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        create_demo_data() 