"""
This script modifies specific parking locations for UI demo purposes
by setting random slot counts and making all slots available.
"""
import random
import sys
import os
import logging

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.parking_location import ParkingLocation
from app.models.parking_slot import ParkingSlot
from sqlalchemy.exc import SQLAlchemyError

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def update_demo_locations():
    """
    Update 6 specific parking locations for demo purposes:
    - Set total_slots to random values between 80-200
    - Set available_slots = total_slots
    """
    # List of locations to update
    location_names = [
        "Alpha One Mall Parking",
        "Himalaya Mall Parking",
        "City Gold Multiplex Parking",
        "Central Mall Parking",
        "Sabarmati Riverfront Parking",
        "ISCON Mall Parking"
    ]
    
    logger.info(f"Updating {len(location_names)} parking locations for demo...")
    
    # Get the locations from the database
    demo_locations = ParkingLocation.query.filter(
        ParkingLocation.name.in_(location_names)
    ).all()
    
    found_locations = [loc.name for loc in demo_locations]
    missing_locations = set(location_names) - set(found_locations)
    
    if missing_locations:
        logger.warning(f"The following locations were not found in the database: {missing_locations}")
        
        # Create missing locations with default values if required
        create_missing = input(f"Do you want to create the missing {len(missing_locations)} locations? (y/n): ")
        if create_missing.lower() == 'y':
            default_ahmedabad_coords = {
                "Alpha One Mall Parking": (23.0469, 72.5308, "Vastrapur"),
                "Himalaya Mall Parking": (23.0478, 72.5438, "Gurukul"),
                "City Gold Multiplex Parking": (23.0383, 72.5483, "Ashram Road"),
                "Central Mall Parking": (23.0365, 72.5559, "Ambawadi"),
                "Sabarmati Riverfront Parking": (23.0508, 72.5757, "Usmanpura"),
                "ISCON Mall Parking": (23.0301, 72.5124, "Satellite")
            }
            
            for loc_name in missing_locations:
                if loc_name in default_ahmedabad_coords:
                    lat, lng, area = default_ahmedabad_coords[loc_name]
                    new_location = ParkingLocation(
                        name=loc_name,
                        address=f"{area}, Ahmedabad",
                        area=area,
                        city="Ahmedabad",
                        state="Gujarat",
                        pincode="380015",
                        latitude=lat,
                        longitude=lng,
                        hourly_rate=25.0,
                        is_24_hours=True
                    )
                    db.session.add(new_location)
                    logger.info(f"Created new location: {loc_name} in {area}")
                    
            # Commit the new locations
            db.session.commit()
            
            # Refresh the list of demo locations
            demo_locations = ParkingLocation.query.filter(
                ParkingLocation.name.in_(location_names)
            ).all()
    
    processed_count = 0
    
    for location in demo_locations:
        logger.info(f"Processing {location.name}...")
        
        try:
            # Generate random number of slots
            new_total_slots = random.randint(80, 200)
            location.total_slots = new_total_slots
            location.available_slots = new_total_slots
            
            # Delete existing slots for this location
            num_deleted = ParkingSlot.query.filter_by(parking_location_id=location.id).delete()
            logger.info(f"- Deleted {num_deleted} existing parking slots")
            
            # Create new slots
            for i in range(1, new_total_slots + 1):
                # Create a new slot
                slot = ParkingSlot(
                    parking_location_id=location.id,
                    slot_number=f"{location.area[:3].upper()}-{i:03d}",
                    is_active=True,
                    is_occupied=False,  # All slots initially available
                    hourly_rate=location.hourly_rate,
                    # Set some slots with specific coordinates for map view
                    latitude=location.latitude + (i / 10000),
                    longitude=location.longitude + (i / 10000)
                )
                db.session.add(slot)
            
            # Commit changes for this location
            db.session.commit()
            logger.info(f"- Created {new_total_slots} available parking slots")
            logger.info(f"- Updated {location.name} total_slots to {new_total_slots}")
            processed_count += 1
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error updating {location.name}: {str(e)}")
    
    # Final message
    if processed_count > 0:
        logger.info(f"Successfully updated {processed_count} locations")
    else:
        logger.warning("No locations were successfully updated")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        update_demo_locations() 