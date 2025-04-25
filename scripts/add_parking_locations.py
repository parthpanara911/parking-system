"""
Script to add sample parking locations in Ahmedabad to the database.
Run this script from the main directory with:
    python -m scripts.add_parking_locations
"""

import os
import sys
from datetime import time

# Add the parent directory to path so we can import our app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.parking_location import ParkingLocation
from app.models.parking_slot import ParkingSlot

def create_parking_locations():
    """Add sample parking locations in Ahmedabad."""
    # Create the app context
    app = create_app()
    
    with app.app_context():
        # Check if we already have parking locations
        existing_count = ParkingLocation.query.count()
        if existing_count > 0:
            print(f"Database already has {existing_count} parking locations. Skipping creation.")
            return
        
        # Sample parking locations in Ahmedabad
        locations = [
            {
                'name': 'Alpha One Mall Parking',
                'address': 'Vastrapur Lake, Vastrapur',
                'area': 'Vastrapur',
                'pincode': '380054',
                'latitude': 23.0469,
                'longitude': 72.5308,
                'total_slots': 100,
                'available_slots': 50,
                'hourly_rate': 30.0,
                'has_covered_parking': True,
                'has_cctv': True,
                'has_security': True,
                'is_24_hours': False,
                'opening_time': time(10, 0),  # 10:00 AM
                'closing_time': time(22, 0),  # 10:00 PM
            },
            {
                'name': 'Himalaya Mall Parking',
                'address': 'Drive In Road, Gurukul',
                'area': 'Gurukul',
                'pincode': '380015',
                'latitude': 23.0478,
                'longitude': 72.5438,
                'total_slots': 80,
                'available_slots': 30,
                'hourly_rate': 25.0,
                'has_covered_parking': True,
                'has_cctv': True,
                'is_24_hours': False,
                'opening_time': time(10, 0),  # 10:00 AM
                'closing_time': time(22, 0),  # 10:00 PM
            },
            {
                'name': 'City Gold Multiplex Parking',
                'address': 'Ashram Road, Navrangpura',
                'area': 'Navrangpura',
                'pincode': '380009',
                'latitude': 23.0337,
                'longitude': 72.5628,
                'total_slots': 60,
                'available_slots': 20,
                'hourly_rate': 20.0,
                'has_covered_parking': True,
                'has_cctv': True,
                'is_24_hours': False,
                'opening_time': time(8, 0),   # 8:00 AM
                'closing_time': time(23, 30), # 11:30 PM
            },
            {
                'name': 'IIM Ahmedabad Parking',
                'address': 'Vastrapur, Ahmedabad',
                'area': 'Vastrapur',
                'pincode': '380015',
                'latitude': 23.0313,
                'longitude': 72.5293,
                'total_slots': 120,
                'available_slots': 80,
                'hourly_rate': 20.0,
                'has_covered_parking': False,
                'has_security': True,
                'is_24_hours': True,
            },
            {
                'name': 'Law Garden Parking',
                'address': 'Netaji Road, Ellisbridge',
                'area': 'Ellisbridge',
                'pincode': '380006',
                'latitude': 23.0256,
                'longitude': 72.5645,
                'total_slots': 50,
                'available_slots': 15,
                'hourly_rate': 15.0,
                'has_covered_parking': False,
                'is_24_hours': True,
            },
            {
                'name': 'Central Mall Parking',
                'address': 'Ambawadi, Ahmedabad',
                'area': 'Ambawadi',
                'pincode': '380015',
                'latitude': 23.0216,
                'longitude': 72.5496,
                'total_slots': 90,
                'available_slots': 40,
                'hourly_rate': 30.0,
                'has_covered_parking': True,
                'has_ev_charging': True,
                'has_disabled_access': True,
                'has_cctv': True,
                'has_security': True,
                'is_24_hours': False,
                'opening_time': time(10, 0),  # 10:00 AM
                'closing_time': time(22, 0),  # 10:00 PM
            },
            {
                'name': 'Ahmedabad One Mall Parking',
                'address': 'Vastrapur, Ahmedabad',
                'area': 'Vastrapur',
                'pincode': '380054',
                'latitude': 23.0454,
                'longitude': 72.5318,
                'total_slots': 150,
                'available_slots': 60,
                'hourly_rate': 40.0,
                'has_covered_parking': True,
                'has_ev_charging': True,
                'has_disabled_access': True,
                'has_cctv': True,
                'has_security': True,
                'is_24_hours': False,
                'opening_time': time(10, 0),  # 10:00 AM
                'closing_time': time(22, 0),  # 10:00 PM
            },
            {
                'name': 'Sabarmati Riverfront Parking',
                'address': 'Riverfront West, Usmanpura',
                'area': 'Usmanpura',
                'pincode': '380013',
                'latitude': 23.0508,
                'longitude': 72.5757,
                'total_slots': 200,
                'available_slots': 120,
                'hourly_rate': 10.0,
                'has_covered_parking': False,
                'is_24_hours': True,
            },
            {
                'name': 'Ahmedabad Railway Station Parking',
                'address': 'Kalupur, Ahmedabad',
                'area': 'Kalupur',
                'pincode': '380002',
                'latitude': 23.0254,
                'longitude': 72.5978,
                'total_slots': 100,
                'available_slots': 30,
                'hourly_rate': 20.0,
                'has_covered_parking': False,
                'has_security': True,
                'is_24_hours': True,
            },
            {
                'name': 'ISCON Mall Parking',
                'address': 'SG Highway, Satellite',
                'area': 'Satellite',
                'pincode': '380015',
                'latitude': 23.0301,
                'longitude': 72.5124,
                'total_slots': 120,
                'available_slots': 50,
                'hourly_rate': 35.0,
                'has_covered_parking': True,
                'has_ev_charging': True,
                'has_disabled_access': True,
                'has_cctv': True,
                'has_security': True,
                'is_24_hours': False,
                'opening_time': time(10, 0),  # 10:00 AM
                'closing_time': time(22, 0),  # 10:00 PM
            }
        ]
        
        # Add locations to database
        created_locations = []
        for loc_data in locations:
            location = ParkingLocation(**loc_data)
            db.session.add(location)
            created_locations.append(location)
        
        # Commit locations to get IDs
        db.session.commit()
        
        # Add parking slots for each location
        for location in created_locations:
            for i in range(1, location.total_slots + 1):
                slot_type = 'standard'
                # Make some slots special types
                if i % 20 == 0:
                    slot_type = 'disabled'
                elif i % 10 == 0:
                    slot_type = 'electric'
                
                # Create the slot
                slot = ParkingSlot(
                    parking_location_id=location.id,
                    slot_number=f"{location.area[:3].upper()}-{i:03d}",
                    slot_type=slot_type,
                    is_active=True,
                    is_occupied=i % 3 == 0,  # Make every 3rd slot occupied for demo
                    hourly_rate=location.hourly_rate,
                    # Set some slots with specific coordinates for large parking lots
                    latitude=location.latitude + (i / 10000),
                    longitude=location.longitude + (i / 10000)
                )
                db.session.add(slot)
        
        # Commit all slots
        db.session.commit()
        
        # Update available slots count for each location
        for location in created_locations:
            location.update_available_slots()
        
        print(f"Created {len(locations)} parking locations with {sum(loc['total_slots'] for loc in locations)} slots")

if __name__ == '__main__':
    create_parking_locations() 