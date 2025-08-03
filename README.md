# Smart Parking System

A Flask-based smart parking  system with multiple features for users, administrators, and parking management.

## Features

- User Registration/Login
- Admin Login
- Parking Slot Booking
- Real-time Slot Availability
- Parking Slot Allotment
- Entry/Exit Ticket Verification
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
- On Exit: Show Ticket 
- Fee Calculation & Payment
- Receipt Generation

### Admin Side
- Admin Login
- Dashboard View (Total Users, Slots, Revenue, Live Status)
- Delete Parking Slots, Bookings
- Monitor Slot Usage
- View and Manage Users

## Setup Project

1. Create and activate a virtual environment:
   ```
   python -m venv venv
   Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Initialize the database:
   ```
   flask db init
   flask db migrate
   flask db upgrade
   ```

5. Run the application:
   ```
   flask run
   ```

