# Smart Parking System

A Flask-based smart parking management system with multiple features for users, administrators, and parking management.

## Features

### Features
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
- Entry 
- Park Vehicle
- On Exit: Show Ticket n
- Fee Calculation & Payment
- Receipt Generation

### Admin Side
- Admin Login
- Dashboard View (Total Users, Slots, Revenue, Live Status)
- Delete Parking Slots
- Monitor Slot Usage
- View and Manage Users

## Project Structure
```
smart_parking_system/
├── app/
│   ├── __init__.py
│   ├── admin/
│   ├── auth/
│   ├── models/
│   ├── parking/
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