# Smart Parking System

A Flask-based smart parking management system with multiple features for users, administrators, and parking management.

## Features

### Basic Features
- User Registration/Login
- Admin Login
- Parking Slot Booking
- Real-time Slot Availability
- Parking Slot Allotment
- Entry and Exit Time Logging
- Parking Fee Calculation
- Bill Generation
- Receipt Download (PDF)
- Admin Dashboard
- User Dashboard

### Advanced Features
- RFID Tag Integration
- License Plate Recognition
- Real-Time Slot Availability with Sensors
- Live CCTV Feed
- Mobile App Integration
- Payment Gateway Integration
- Dynamic Pricing
- User Reviews and Feedback
- Loyalty Points

### Innovative Features
- Predictive Slot Availability (ML-based)
- Carbon Footprint Estimation
- Gamification for Eco-parking
- Voice Command Booking
- Integration with Maps
- EV Charging Slot Monitoring
- Nearby Services Suggestion

## Workflow

### User/Driver Side
- Open App or Web Interface
- Register/Login
- Enter Destination/Location
- Search and View Available Parking Slots
- Filter as Needed
- Select and Book Slot
- Confirm Booking (with Payment)
- Receive Booking Confirmation
- Navigate to Parking
- Entry using QR Code/RFID/Plate Recognition
- Park Vehicle
- On Exit: Scan QR or Automatic Detection
- Fee Calculation & Payment
- Receipt Generation

### Admin Side
- Admin Login
- Dashboard View (Total Users, Slots, Revenue, Live Status)
- Add/Edit/Delete Parking Slots
- Monitor Slot Usage
- View and Manage Users
- Resolve User Complaints
- View Reports and Statistics
- Manage Payments & Refunds

## Project Structure
```
smart_parking_system/
├── app/
│   ├── __init__.py
│   ├── admin/
│   ├── api/
│   ├── auth/
│   ├── models/
│   ├── parking/
│   ├── payment/
│   ├── notification/
│   ├── reports/
│   ├── ml/
│   ├── views/
│   ├── static/
│   ├── templates/
│   └── utils/
├── config/
├── migrations/
├── tests/
├── .env
├── requirements.txt
└── run.py
```

## Setup and Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/smart_parking_system.git
   cd smart_parking_system
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Initialize the database:
   ```
   flask db init
   flask db migrate
   flask db upgrade
   ```

6. Run the application:
   ```
   flask run
   ```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Database Schema Cleanup

The database schema has been simplified for UI testing with the following changes:

### Removed Columns
- From `parking_locations` table:
  - has_covered_parking
  - has_ev_charging
  - has_disabled_access
  - has_cctv
  - has_security
  - rating

- From `parking_slots` table:
  - level
  - slot_type
  - slot_size
  - sensor_id

- From `vehicles` table:
  - make
  - model

### Dropped Tables
- payments
- reviews
- wallets
- wallet_transactions
- sensor_data

### Modified Parking Locations
The following 6 locations have been prepared for UI testing:
- Alpha One Mall Parking
- Himalaya Mall Parking
- City Gold Multiplex Parking
- Central Mall Parking
- Sabarmati Riverfront Parking
- ISCON Mall Parking

Each location has a random number of slots between 80-200, and all slots are set as available.

### Running the Updates

First, you can check the current state of your database with:

```bash
python scripts/validate_schema.py
```

This will show you what changes have already been applied and what still needs to be done.

#### Option 1: Automatic Update (Recommended)

To apply all changes at once, use the cleanup script:

```bash
python cleanup_and_update.py
```

#### Option 2: Manual Steps

Or follow these individual steps:

1. Run the migration to update the database schema:

```bash
flask db upgrade
```

2. Update the demo parking locations with random slot counts:

```bash
python scripts/update_demo_locations.py
```

#### Option 3: Direct SQL Method (If Options 1 & 2 Fail)

If you encounter foreign key constraint issues with the migration, you can use the manual cleanup script:

```bash
python scripts/manually_drop_tables.py
```

This script will:
1. Temporarily disable foreign key checks
2. Drop the tables and columns directly using SQL
3. Update the migration version record
4. Re-enable foreign key checks

After running the manual cleanup, you can proceed with updating the demo locations:

```bash
python scripts/update_demo_locations.py
```
