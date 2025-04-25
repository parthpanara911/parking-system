"""
Script to fetch parking locations from OpenStreetMap (Overpass API) for Ahmedabad
and add them to the database.
"""

import os
import sys
import requests
import random
from datetime import time, datetime
from geopy.geocoders import Nominatim

# Add the parent directory to path so we can import our app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.parking_location import ParkingLocation
from app.models.parking_slot import ParkingSlot

# Overpass API endpoint
OVERPASS_API = "https://overpass-api.de/api/interpreter"

# Ahmedabad bounding box (south, west, north, east)
AHMEDABAD_BBOX = "22.9, 72.4, 23.1, 72.7"

def fetch_from_overpass():
    """Fetch parking locations from Overpass API."""
    print("Fetching parking locations from OpenStreetMap...")
    
    # Query for parking in Ahmedabad
    query = """
    [out:json][timeout:25];
    area["name"="Ahmedabad"]["boundary"="administrative"]["admin_level"="8"]->.searchArea;
    (
    node["amenity"="parking"](area.searchArea);
    way["amenity"="parking"](area.searchArea);
    relation["amenity"="parking"](area.searchArea);
    );
    out center;
    """

    # f"""
    # [out:json];
    # (
    #   node["amenity"="parking"]({AHMEDABAD_BBOX});
    #   way["amenity"="parking"]({AHMEDABAD_BBOX});
    #   relation["amenity"="parking"]({AHMEDABAD_BBOX});
    # );
    # out center;
    # """
    
    try:
        response = requests.post(OVERPASS_API, data={"data": query})
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data from Overpass API: {e}")
        return None

def generate_area_name(lat, lon):
    """Generate area name for a location using reverse geocoding."""
    try:
        geolocator = Nominatim(user_agent="smart_parking_system")
        location = geolocator.reverse(f"{lat}, {lon}", exactly_one=True)
        address = location.raw.get('address', {})
        
        # Try to get neighborhood or suburb
        area = address.get('suburb') or address.get('neighbourhood') or address.get('residential')
        
        # If no specific area found, use a generic one
        if not area:
            return "Central Ahmedabad"
        
        return area
    except Exception as e:
        print(f"Error with geocoding: {e}")
        return "Ahmedabad"

def generate_parking_details():
    """Generate random parking details."""
    # Random hourly rates
    hourly_rates = [10, 15, 20, 25, 30, 35, 40, 50]
    
    # Random slot counts
    slot_counts = [30, 50, 60, 80, 100, 120, 150, 200, 250]
    
    # Random amenities
    has_covered = random.choice([True, False])
    has_ev = random.choice([True, False, False])  # Less common
    has_disabled = random.choice([True, False])
    has_cctv = random.choice([True, True, False])  # More common
    has_security = random.choice([True, True, False])  # More common
    
    # Random opening hours
    is_24_hours = random.choice([True, False, False])  # Less common
    
    if is_24_hours:
        opening_time = time(0, 0)
        closing_time = time(23, 59)
    else:
        opening_hour = random.choice([6, 7, 8, 9, 10])
        closing_hour = random.choice([18, 19, 20, 21, 22])
        opening_time = time(opening_hour, 0)
        closing_time = time(closing_hour, 0)
    
    return {
        'hourly_rate': random.choice(hourly_rates),
        'total_slots': random.choice(slot_counts),
        'has_covered_parking': has_covered,
        'has_ev_charging': has_ev,
        'has_disabled_access': has_disabled,
        'has_cctv': has_cctv,
        'has_security': has_security,
        'is_24_hours': is_24_hours,
        'opening_time': opening_time,
        'closing_time': closing_time,
    }

def process_parking_data(data):
    """Process parking data from Overpass API."""
    parking_locations = []
    
    if not data or 'elements' not in data:
        print("No data returned from Overpass API")
        return parking_locations
    
    for element in data['elements']:
        try:
            # Get coordinates
            if element['type'] == 'node':
                lat = element['lat']
                lon = element['lon']
            else:  # way or relation
                lat = element.get('center', {}).get('lat')
                lon = element.get('center', {}).get('lon')
            
            if not lat or not lon:
                continue
            
            # Get tags data
            tags = element.get('tags', {})
            name = tags.get('name')
            
            # Skip if no name
            # if not name:
            #     name = f"Parking {element['id']}"
            if not name:
                area = generate_area_name(lat, lon)
                name = f"{area} Public Parking"
            
            # Generate area name
            area = generate_area_name(lat, lon)
            
            # Generate address
            address = tags.get('addr:full', f"{area}, Ahmedabad")
            
            # Generate other details
            details = generate_parking_details()
            
            # Create parking location dictionary
            parking_location = {
                'name': name,
                'address': address,
                'area': area,
                'city': 'Ahmedabad',
                'state': 'Gujarat',
                'pincode': tags.get('addr:postcode', '380001'),
                'latitude': lat,
                'longitude': lon,
                'available_slots': random.randint(1, details['total_slots']),
                'image_url': None,  # Will use default image
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                **details
            }
            
            parking_locations.append(parking_location)
            
        except Exception as e:
            print(f"Error processing element {element.get('id')}: {e}")
            continue
    
    return parking_locations

def fallback_generate_data():
    """Generate random parking locations in Ahmedabad if API fails."""
    print("Generating fallback data...")
    
    # Areas in Ahmedabad
    areas = [
        "Navrangpura", "Satellite", "Vastrapur", "Thaltej", "Bodakdev", 
        "CG Road", "Ellisbridge", "Paldi", "Ambawadi", "Gurukul", 
        "Maninagar", "Ghatlodia", "Science City", "Chandkheda", "Motera",
        "Bopal", "South Bopal", "Prahlad Nagar", "Jodhpur", "Vejalpur",
        "Naranpura", "Sabarmati", "Usmanpura", "Memnagar", "Ranip"
    ]
    
    # Some location types
    location_types = [
        "Mall Parking", "Commercial Complex", "Public Parking", 
        "Metro Station Parking", "Municipal Parking", "Hospital Parking",
        "Shopping Center", "Entertainment Zone", "Market Parking", "Stadium Parking"
    ]
    
    # Base coordinates for Ahmedabad
    base_lat = 23.0225
    base_lng = 72.5714
    
    parking_locations = []
    
    # Generate 50 random parking locations
    for i in range(50):
        area = random.choice(areas)
        location_type = random.choice(location_types)
        
        # Random name
        if random.random() < 0.5:
            name = f"{area} {location_type}"
        else:
            name = f"{random.choice(['Royal', 'City', 'Smart', 'Premium', 'Secure', 'Central', 'Metro'])} {location_type}"
        
        # Random coordinates with slight variations
        lat = base_lat + (random.random() - 0.5) * 0.1
        lng = base_lng + (random.random() - 0.5) * 0.1
        
        # Generate other details
        details = generate_parking_details()
        
        parking_location = {
            'name': name,
            'address': f"{area}, Ahmedabad",
            'area': area,
            'city': 'Ahmedabad',
            'state': 'Gujarat',
            'pincode': f"38{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}",
            'latitude': lat,
            'longitude': lng,
            'available_slots': random.randint(1, details['total_slots']),
            'image_url': None,  # Will use default image
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            **details
        }
        
        parking_locations.append(parking_location)
    
    return parking_locations

def add_parking_slots(location):
    """Add parking slots for a location."""
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
            is_occupied=i > location.available_slots,  # Make the correct number occupied
            hourly_rate=location.hourly_rate,
            # Set some slots with specific coordinates for large parking lots
            latitude=location.latitude + (i / 10000),
            longitude=location.longitude + (i / 10000)
        )
        db.session.add(slot)

def fetch_and_save_parking_locations():
    """Main function to fetch and save parking locations."""
    # Create the app context
    app = create_app()
    
    with app.app_context():
        # Check if we already have parking locations
        existing_count = ParkingLocation.query.count()
        if existing_count > 0:
            print(f"Database already has {existing_count} parking locations.")
            choice = input("Do you want to add more locations? (y/n): ").lower()
            if choice != 'y':
                return
        
        # Try to fetch from API first
        data = fetch_from_overpass()
        parking_locations = []
        
        if data and 'elements' in data:
            parking_locations = process_parking_data(data)
            
        # If API fails or returns no data, generate random data
        if not parking_locations:
            parking_locations = fallback_generate_data()
        
        print(f"Adding {len(parking_locations)} parking locations to database...")
        
        # Add locations to database
        created_locations = []
        for loc_data in parking_locations:
            # Check if location already exists (by coordinates)
            existing = ParkingLocation.query.filter_by(
                latitude=loc_data['latitude'], 
                longitude=loc_data['longitude']
            ).first()
            
            if existing:
                if existing.name.startswith("Parking "):
                    area = generate_area_name(loc_data['latitude'], loc_data['longitude'])
                    existing.name = f"{area} Public Parking"
                    db.session.commit()
                    print(f"Updated name of existing location: {existing.name}")
                else:
                    print(f"Skipping existing location: {loc_data['name']}")
                continue

                
            location = ParkingLocation(**loc_data)
            db.session.add(location)
            created_locations.append(location)
        
        # Commit locations to get IDs
        db.session.commit()
        
        # Add parking slots for each location
        for location in created_locations:
            add_parking_slots(location)
        
        # Commit all slots
        db.session.commit()
        
        # Update available slots count for each location
        for location in created_locations:
            location.update_available_slots()
        
        print(f"Successfully added {len(created_locations)} parking locations")

if __name__ == '__main__':
    fetch_and_save_parking_locations() 