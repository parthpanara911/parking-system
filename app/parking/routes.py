from flask import (
    Blueprint,
    render_template,
    jsonify,
    request,
    current_app,
    redirect,
    url_for,
    flash,
    session,
    make_response,
)
from flask_login import login_required, current_user
from app.models.parking_location import ParkingLocation
from app.models.parking_slot import ParkingSlot
from app.models.booking import Booking
from app import db
from datetime import datetime, timedelta, date, time
import random
import re
import qrcode
from io import BytesIO
import base64
from fpdf import FPDF
import tempfile
import os

# Create the parking blueprint
parking = Blueprint("parking", __name__, url_prefix="/parking")


@parking.route("/find")
@login_required
def find_parking():
    """Parking finder page that shows locations on map and in list view."""
    return render_template("parking/find.html")


@parking.route("/api/locations")
@login_required
def get_locations():
    """API endpoint to get all parking locations as JSON."""
    locations = ParkingLocation.get_all_locations()
    return jsonify([location.to_dict() for location in locations])


@parking.route("/api/locations/<int:location_id>")
@login_required
def get_location(location_id):
    """API endpoint to get a specific parking location as JSON."""
    location = ParkingLocation.get_by_id(location_id)
    if location:
        return jsonify(location.to_dict())
    return jsonify({"error": "Location not found"}), 404


@parking.route("/booking_details/<int:parking_id>", methods=["GET", "POST"])
@login_required
def booking_details(parking_id):
    """
    Handle booking details form.
    GET: Show the form with date and time selection.
    POST: Process the form data and redirect to the slot selection page.
    """
    # Get the parking location
    location = ParkingLocation.get_by_id(parking_id)
    if not location:
        flash("Parking location not found", "danger")
        return redirect(url_for("parking.find_parking"))

    # Check if booking_id is in the request parameters (for editing an existing booking)
    booking_id = request.args.get("booking_id")
    booking = None

    if booking_id:
        booking = Booking.get_by_id(booking_id)
        if not booking or booking.user_id != current_user.id:
            flash("Invalid booking", "danger")
            return redirect(url_for("parking.find_parking"))

    # For POST request, process the form
    if request.method == "POST":
        # Get form data
        date_str = request.form.get("date")
        start_time_str = request.form.get("start_time")
        end_time_str = request.form.get("end_time")
        vehicle_number = request.form.get("vehicle_number")

        # Validate form data
        if not all([date_str, start_time_str, end_time_str, vehicle_number]):
            flash("All fields are required", "danger")
            return render_template(
                "parking/booking_details.html", location=location, booking=booking
            )

        # Validate vehicle number format (Indian format)
        if not re.match(r"^[A-Z]{2}[0-9]{1,2}[A-Z]{1,2}[0-9]{4}$", vehicle_number):
            flash(
                "Please enter a valid Indian vehicle number (e.g., GJ01AB1234)",
                "danger",
            )
            return render_template(
                "parking/booking_details.html", location=location, booking=booking
            )

        # Convert to datetime objects for validation
        try:
            booking_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            start_datetime = datetime.strptime(
                f"{date_str} {start_time_str}", "%Y-%m-%d %H:%M"
            )
            end_datetime = datetime.strptime(
                f"{date_str} {end_time_str}", "%Y-%m-%d %H:%M"
            )

            # Extract time objects for database
            start_time_obj = time(start_datetime.hour, start_datetime.minute)
            end_time_obj = time(end_datetime.hour, end_datetime.minute)

            # Check if booking date is not in the past
            if booking_date < datetime.now().date():
                flash("Booking date cannot be in the past", "danger")
                return render_template(
                    "parking/booking_details.html", location=location, booking=booking
                )

            # Check if start time is before end time
            if start_datetime >= end_datetime:
                flash("End time must be after start time", "danger")
                return render_template(
                    "parking/booking_details.html", location=location, booking=booking
                )

            # Check if start time is in the future
            if start_datetime < datetime.now():
                flash("Start time must be in the future", "danger")
                return render_template(
                    "parking/booking_details.html", location=location, booking=booking
                )

            # Check if booking duration is at least 1 hour
            duration_hours = (end_datetime - start_datetime).total_seconds() / 3600
            if duration_hours < 1:
                flash("Booking must be for at least 1 hour", "danger")
                return render_template(
                    "parking/booking_details.html", location=location, booking=booking
                )

            # Check if booking is within parking location hours
            # Convert opening and closing times to time objects
            opening_time = datetime.strptime(location.opening_time, "%H:%M").time()
            closing_time = datetime.strptime(location.closing_time, "%H:%M").time()

            # Check if start time is after opening time
            if start_time_obj < opening_time:
                flash(f"Parking location opens at {location.opening_time}", "danger")
                return render_template(
                    "parking/booking_details.html", location=location, booking=booking
                )

            # Check if end time is before closing time
            if end_time_obj > closing_time:
                flash(f"Parking location closes at {location.closing_time}", "danger")
                return render_template(
                    "parking/booking_details.html", location=location, booking=booking
                )

            # Calculate cost
            total_price = duration_hours * location.hourly_rate
            # Round to nearest whole number based on tenths digit
            total_price = round(total_price)

            # Create or update booking record in database
            if booking:
                # Update existing booking
                booking.booking_date = booking_date
                booking.start_time = start_time_obj
                booking.end_time = end_time_obj
                booking.duration_hours = round(duration_hours, 2)
                booking.total_price = total_price
                booking.vehicle_number = vehicle_number
                db.session.commit()
            else:
                # Create new booking
                booking = Booking.create_booking(
                    parking_location_id=parking_id,
                    booking_date=booking_date,
                    start_time=start_time_obj,
                    end_time=end_time_obj,
                    duration_hours=round(duration_hours, 2),
                    total_price=total_price,
                    vehicle_number=vehicle_number,
                )

            # Redirect to slot selection page with booking ID
            return redirect(url_for("parking.booking_slot", booking_id=booking.id))

        except ValueError as e:
            current_app.logger.error(f"Date/time validation error: {str(e)}")
            flash("Invalid date or time format", "danger")
            return render_template(
                "parking/booking_details.html", location=location, booking=booking
            )

    # For GET request, show the form
    return render_template(
        "parking/booking_details.html", location=location, booking=booking
    )


@parking.route("/booking_slot", methods=["GET", "POST"])
@login_required
def booking_slot():
    """
    Handle slot selection.
    GET: Show available slots.
    POST: Process the selected slot and redirect to payment.
    """
    # Get booking ID from request parameters
    booking_id = request.args.get("booking_id")
    if not booking_id:
        flash("Invalid booking", "danger")
        return redirect(url_for("parking.find_parking"))

    # Get booking from database
    booking = Booking.get_by_id(booking_id)
    if not booking or booking.user_id != current_user.id:
        flash("Invalid booking", "danger")
        return redirect(url_for("parking.find_parking"))

    # Get parking location
    location = ParkingLocation.get_by_id(booking.parking_location_id)
    if not location:
        flash("Parking location not found", "danger")
        return redirect(url_for("parking.find_parking"))

    # Auto-release any expired slots before showing the slot selection page
    Booking.release_expired_slots()
    # ParkingSlot.release_slot(slot_id)

    if request.method == "POST":
        # Get selected slot
        slot_id = request.form.get("slot_id")
        vehicle_type = request.form.get("vehicle_type")

        if not slot_id or not vehicle_type:
            flash("Please select a parking slot", "danger")
            return render_template(
                "parking/booking_slot.html", location=location, booking=booking
            )

        # Get the slot and check if it's available
        slot = ParkingSlot.get_by_id(slot_id)
        if not slot or not slot.is_available:
            flash("This slot is no longer available", "danger")
            return render_template(
                "parking/booking_slot.html", location=location, booking=booking
            )

        # Update booking with slot details
        booking.update_slot_details(slot_id, vehicle_type)

        # Reserve the slot
        ParkingSlot.reserve_slot(slot_id)

        # For now, redirect to a success page
        # In a real application, you would proceed to a payment page
        flash(
            "Slot successfully reserved! Proceed to payment",
            "success",
        )
        return redirect(url_for("parking.booking_confirmation", booking_id=booking.id))

    # For GET request, show available slots
    return render_template(
        "parking/booking_slot.html", location=location, booking=booking
    )


@parking.route("/booking_confirmation", methods=["GET", "POST"])
@login_required
def booking_confirmation():
    """Display booking confirmation details and handle payment."""
    booking_id = request.args.get("booking_id")
    if not booking_id:
        flash("Invalid booking", "danger")
        return redirect(url_for("parking.find_parking"))

    booking = Booking.get_by_id(booking_id)
    if not booking or booking.user_id != current_user.id:
        flash("Invalid booking", "danger")
        return redirect(url_for("parking.find_parking"))

    location = ParkingLocation.get_by_id(booking.parking_location_id)
    slot = None
    if booking.parking_slot_id:
        slot = ParkingSlot.get_by_id(booking.parking_slot_id)

    # Handle POST request (payment processing)
    if request.method == "POST":
        payment_method = request.form.get("payment_method")

        if not payment_method:
            flash("Please select a payment method", "danger")
            return render_template(
                "parking/booking_confirmation.html",
                booking=booking,
                location=location,
                slot=slot,
            )

        # Handle different payment methods
        if payment_method == "cash":
            booking.update_payment_details(payment_method, "pending")
            booking.booking_status = "confirmed"
            db.session.commit()

            flash("Booking confirmed! Please pay at the parking location.", "success")
            return redirect(url_for("parking.parking_ticket", booking_id=booking.id))

        elif payment_method == "razorpay":
            # In a real application, you would integrate with RazorPay API here
            # For now, just simulate a successful payment
            booking.update_payment_details(payment_method, "paid")

            flash("Payment successful! Your booking has been confirmed.", "success")
            return redirect(url_for("parking.parking_ticket", booking_id=booking.id))

        else:
            flash("Invalid payment method", "danger")
            return render_template(
                "parking/booking_confirmation.html",
                booking=booking,
                location=location,
                slot=slot,
            )

    # For GET request, show the confirmation page
    return render_template(
        "parking/booking_confirmation.html",
        booking=booking,
        location=location,
        slot=slot,
    )


@parking.route("/api/slots/<int:location_id>/<vehicle_type>")
@login_required
def get_slots(location_id, vehicle_type):
    """API endpoint to get available slots by location and vehicle type."""
    if vehicle_type not in ["two-wheeler", "four-wheeler"]:
        return jsonify({"error": "Invalid vehicle type"}), 400

    slots = ParkingSlot.get_available_slots(location_id, vehicle_type)
    return jsonify([slot.to_dict() for slot in slots])


@parking.route("/api/all_slots/<int:location_id>/<vehicle_type>")
@login_required
def get_all_slots(location_id, vehicle_type):
    """API endpoint to get all slots (available and unavailable) by location and vehicle type."""
    if vehicle_type not in ["two-wheeler", "four-wheeler"]:
        return jsonify({"error": "Invalid vehicle type"}), 400

    slots = ParkingSlot.get_all_slots(location_id, vehicle_type)
    return jsonify([slot.to_dict() for slot in slots])


@parking.route("/ticket/<int:booking_id>")
@login_required
def parking_ticket(booking_id):
    """Generate downloadable PDF parking ticket"""
    # Get the booking details
    booking = Booking.query.get_or_404(booking_id)

    # Ensure the booking belongs to the current user
    if booking.user_id != current_user.id:
        flash("You don't have permission to access this ticket", "danger")
        return redirect(url_for("main.index"))

    # Get the associated parking location
    location = ParkingLocation.query.get(booking.parking_location_id)
    parking_slot = ParkingSlot.query.get_or_404(booking.parking_slot_id)

    # Create a QR code with booking details
    # Create QR code data with booking information
    qr_data = f"Booking ID: {booking.id}\nLocation: {location.name}\nVehicle: {booking.vehicle_number}\nDate: {booking.booking_date.strftime('%Y-%m-%d')}\nTime: {booking.start_time.strftime('%H:%M')} to {booking.end_time.strftime('%H:%M')}\nSlot: {parking_slot.slot_number}"

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Save QR code to BytesIO buffer
    buffer = BytesIO()
    img.save(buffer)
    buffer.seek(0)

    # Generate base64 string for the QR code image
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    # Calculate duration and total price - use parking_slot rate instead of location rate
    duration_hours = (booking.end_time.hour - booking.start_time.hour) + (
        booking.end_time.minute - booking.start_time.minute
    ) / 60
    total_price = duration_hours * parking_slot.hourly_rate
    # Round to nearest whole number based on tenths digit
    total_price = round(total_price)

    # Render ticket HTML template
    return render_template(
        "parking/ticket.html",
        booking=booking,
        location=location,
        parking_slot=parking_slot,
        qr_code=qr_code_base64,
        duration_hours=round(duration_hours, 1),
        total_price=total_price,
    )


@parking.route("/ticket/<int:booking_id>/pdf")
@login_required
def parking_ticket_pdf(booking_id):
    """Generate PDF parking ticket for download"""
    # Get the booking details
    booking = Booking.query.get_or_404(booking_id)

    # Ensure the booking belongs to the current user
    if booking.user_id != current_user.id:
        flash("You don't have permission to access this ticket", "danger")
        return redirect(url_for("main.index"))

    # Get the associated parking location
    location = ParkingLocation.query.get(booking.parking_location_id)
    parking_slot = ParkingSlot.query.get_or_404(booking.parking_slot_id)

    # Create QR code
    import qrcode
    from io import BytesIO

    # Create QR code data with booking information
    qr_data = f"Booking ID: {booking.id}\nLocation: {location.name}\nVehicle: {booking.vehicle_number}\nDate: {booking.booking_date.strftime('%Y-%m-%d')}\nTime: {booking.start_time.strftime('%H:%M')} to {booking.end_time.strftime('%H:%M')}\nSlot: {parking_slot.slot_number}"

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Save QR code to a temporary file
    qr_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    img.save(qr_file.name)

    # Calculate duration and total price - use parking_slot rate instead of location rate
    duration_hours = (booking.end_time.hour - booking.start_time.hour) + (
        booking.end_time.minute - booking.start_time.minute
    ) / 60
    total_price = duration_hours * parking_slot.hourly_rate
    # Round to nearest whole number based on tenths digit
    total_price = round(total_price)

    # Create PDF
    pdf = FPDF()
    pdf.add_page()

    # Add title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, "PARKING TICKET", 0, 1, "C")

    # Add booking details
    pdf.set_font("Arial", "", 12)
    pdf.cell(190, 10, f"Booking ID: {booking.id}", 0, 1)
    pdf.cell(190, 10, f"Parking Location: {location.name}", 0, 1)
    pdf.cell(190, 10, f"Address: {location.address}", 0, 1)
    pdf.cell(190, 10, f"Vehicle Number: {booking.vehicle_number}", 0, 1)
    pdf.cell(190, 10, f"Vehicle Type: {booking.vehicle_type}", 0, 1)
    pdf.cell(190, 10, f'Date: {booking.booking_date.strftime("%Y-%m-%d")}', 0, 1)
    pdf.cell(
        190,
        10,
        f'Time: {booking.start_time.strftime("%H:%M")} to {booking.end_time.strftime("%H:%M")}',
        0,
        1,
    )
    pdf.cell(190, 10, f"Slot Number: {parking_slot.slot_number}", 0, 1)
    pdf.cell(190, 10, f"Duration: {round(duration_hours, 1)} hours", 0, 1)
    pdf.cell(190, 10, f"Total Price: Rs.{round(total_price, 2)}", 0, 1)
    pdf.cell(190, 10, f"Payment Status: {booking.payment_status.title()}", 0, 1)

    # Add QR code
    pdf.image(qr_file.name, x=75, y=160, w=60)

    # Add instructions
    pdf.set_font("Arial", "I", 10)
    pdf.cell(190, 10, "Instructions:", 0, 1)
    pdf.multi_cell(
        190,
        5,
        "1. Show this ticket to the parking attendant.\n2. Please park your vehicle in the designated slot.\n3. Contact support at support@smartparking.com for assistance.",
    )

    # Create response
    response = make_response(pdf.output(dest="S").encode("latin1"))
    response.headers.set(
        "Content-Disposition",
        f"attachment",
        filename=f"parking_ticket_{booking.id}.pdf",
    )
    response.headers.set("Content-Type", "application/pdf")

    return response


def seed_parking_locations():
    """
    Seed the database with initial parking locations.
    This function is called during app initialization if no locations exist.
    """
    # Only seed if there are no existing locations
    if ParkingLocation.query.count() == 0:
        locations_data = [
            {
                "name": "Alpha One Mall Parking",
                "address": "Vastrapur Lake, Ahmedabad, Gujarat",
                "area": "Vastrapur",
                "city": "Ahmedabad",
                "state": "Gujarat",
                "pincode": "380015",
                "latitude": 23.0372,
                "longitude": 72.5324,
                "total_slots": 150,
                "available_slots": 150,
                "hourly_rate": 50.0,
                "opening_time": "10:00",
                "closing_time": "22:00",
                "image_url": "/static/images/parking/alpha_one.jpg",
            },
            {
                "name": "Himalaya Mall Parking",
                "address": "Drive In Road, Ahmedabad, Gujarat",
                "area": "Drive In Road",
                "city": "Ahmedabad",
                "state": "Gujarat",
                "pincode": "380054",
                "latitude": 23.0463,
                "longitude": 72.5321,
                "total_slots": 120,
                "available_slots": 120,
                "hourly_rate": 30.0,
                "opening_time": "09:00",
                "closing_time": "23:00",
                "image_url": "/static/images/parking/himalaya_mall.jpg",
            },
            {
                "name": "Palladium Mall Parking",
                "address": "Thaltej, Ahmedabad, Gujarat",
                "area": "Thaltej",
                "city": "Ahmedabad",
                "state": "Gujarat",
                "pincode": "380054",
                "latitude": 23.0458,
                "longitude": 72.5095,
                "total_slots": 200,
                "available_slots": 200,
                "hourly_rate": 50.0,
                "opening_time": "10:00",
                "closing_time": "22:00",
                "image_url": "/static/images/parking/palladium_mall.jpg",
            },
            {
                "name": "Central Mall Parking",
                "address": "Ambawadi, Ahmedabad, Gujarat",
                "area": "Ambawadi",
                "city": "Ahmedabad",
                "state": "Gujarat",
                "pincode": "380015",
                "latitude": 23.0348,
                "longitude": 72.5578,
                "total_slots": 100,
                "available_slots": 100,
                "hourly_rate": 30.0,
                "opening_time": "09:30",
                "closing_time": "22:30",
                "image_url": "/static/images/parking/central_mall.jpg",
            },
            {
                "name": "Sabarmati Riverfront Parking",
                "address": "Sabarmati Riverfront, Ahmedabad, Gujarat",
                "area": "Sabarmati",
                "city": "Ahmedabad",
                "state": "Gujarat",
                "pincode": "380009",
                "latitude": 23.0225,
                "longitude": 72.5714,
                "total_slots": 180,
                "available_slots": 180,
                "hourly_rate": 30.0,
                "opening_time": "06:00",
                "closing_time": "23:00",
                "image_url": "/static/images/parking/riverfront.jpg",
            },
            {
                "name": "ISCON Mall Parking",
                "address": "SG Highway, Ahmedabad, Gujarat",
                "area": "SG Highway",
                "city": "Ahmedabad",
                "state": "Gujarat",
                "pincode": "380015",
                "latitude": 23.0331,
                "longitude": 72.5109,
                "total_slots": 140,
                "available_slots": 140,
                "hourly_rate": 40.0,
                "opening_time": "10:00",
                "closing_time": "22:00",
                "image_url": "/static/images/parking/iscon_mall.jpg",
            },
        ]

    try:
        # Check if locations exist, if so update them
        existing_locations = ParkingLocation.query.all()
        if existing_locations:
            current_app.logger.info("Updating parking locations with new hourly rates")
            # Update existing locations with new rates
            for i, location in enumerate(existing_locations):
                if i < len(locations_data):
                    location.hourly_rate = locations_data[i]["hourly_rate"]

            # Also update hourly rate for parking slots
            slots = ParkingSlot.query.all()
            for slot in slots:
                location = ParkingLocation.query.get(slot.parking_location_id)
                if slot.vehicle_type == "two-wheeler":
                    slot.hourly_rate = (
                        location.hourly_rate * 0.5
                    )  # 50% of the standard rate
                else:
                    slot.hourly_rate = location.hourly_rate

            db.session.commit()
            current_app.logger.info(
                "Updated parking locations and slots with new hourly rates"
            )
        else:
            # Only seed if there are no existing locations
            current_app.logger.info("Seeding parking locations")
            for location_data in locations_data:
                location = ParkingLocation(**location_data)
                db.session.add(location)

            db.session.commit()
            current_app.logger.info("Seeded parking locations successfully")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error with parking locations: {str(e)}")


def seed_parking_slots():
    """
    Seed the database with parking slots for each location.
    This function is called during app initialization if no slots exist.
    """
    # Only seed if there are no existing slots
    if ParkingSlot.query.count() == 0:
        # Get all parking locations
        locations = ParkingLocation.get_all_locations()

        for location in locations:
            # Calculate number of slots for each vehicle type
            two_wheeler_count = int(location.total_slots * 0.4)  # 40% for two-wheelers
            four_wheeler_count = (
                location.total_slots - two_wheeler_count
            )  # 60% for four-wheelers

            # Create two-wheeler slots
            for i in range(1, two_wheeler_count + 1):
                slot = ParkingSlot(
                    parking_location_id=location.id,
                    vehicle_type="two-wheeler",
                    slot_number=f"T{i:03d}",  # Format: T001, T002, etc.
                    is_available=True,
                    is_reserved=False,
                    hourly_rate=location.hourly_rate * 0.5,  # 50% of the standard rate
                )
                db.session.add(slot)

            # Create four-wheeler slots
            for i in range(1, four_wheeler_count + 1):
                slot = ParkingSlot(
                    parking_location_id=location.id,
                    vehicle_type="four-wheeler",
                    slot_number=f"F{i:03d}",  # Format: F001, F002, etc.
                    is_available=True,
                    is_reserved=False,
                    hourly_rate=location.hourly_rate,
                )
                db.session.add(slot)

        try:
            db.session.commit()
            current_app.logger.info("Seeded parking slots successfully")
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error seeding parking slots: {str(e)}")
