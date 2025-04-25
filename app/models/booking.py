from datetime import datetime
from app import db
from flask_login import current_user


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    parking_location_id = db.Column(
        db.Integer, db.ForeignKey("parking_locations.id"), nullable=False
    )
    parking_slot_id = db.Column(
        db.Integer, db.ForeignKey("parking_slots.id"), nullable=True
    )  # Can be null initially until slot is selected
    vehicle_number = db.Column(db.String(20), nullable=False)
    vehicle_type = db.Column(
        db.String(20), nullable=True
    )  # Can be null initially until slot is selected
    booking_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    duration_hours = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=True)
    payment_status = db.Column(db.String(20), default="pending", nullable=False)
    booking_status = db.Column(db.String(20), default="pending", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Define relationships
    user = db.relationship("User", backref="bookings")
    parking_location = db.relationship("ParkingLocation", backref="bookings")
    parking_slot = db.relationship("ParkingSlot", backref="bookings")

    def __repr__(self):
        return f"<Booking #{self.id} for User #{self.user_id} at Location #{self.parking_location_id}>"

    @classmethod
    def get_by_id(cls, booking_id):
        """Get a booking by ID."""
        return cls.query.get(booking_id)

    @classmethod
    def get_user_bookings(cls, user_id):
        """Get all bookings for a specific user."""
        return (
            cls.query.filter_by(user_id=user_id).order_by(cls.created_at.desc()).all()
        )

    @classmethod
    def create_booking(cls, **kwargs):
        """Create a new booking"""
        booking = cls(user_id=current_user.id, **kwargs)
        booking.booking_status = "pending"
        booking.payment_status = "pending"
        db.session.add(booking)
        db.session.commit()
        return booking

    @classmethod
    def release_expired_slots(cls):
        """Release slots for bookings that have ended"""
        now = datetime.now()
        current_date = now.date()
        current_time = now.time()

        # Find confirmed bookings where end time has passed but slot is still reserved
        expired_bookings = cls.query.filter(
            cls.booking_date <= current_date,
            cls.end_time <= current_time,
            cls.booking_status == "confirmed",
        ).all()

        from app.models.parking_slot import ParkingSlot
        from app.models.parking_location import ParkingLocation

        # Release each slot
        for booking in expired_bookings:
            if booking.parking_slot_id:
                # Update booking status to completed
                booking.booking_status = "completed"

                # Release the slot
                slot = ParkingSlot.get_by_id(booking.parking_slot_id)
                if slot and not slot.is_available:
                    slot.is_available = True
                    slot.is_reserved = False

                    # Update available slots count in the parking location
                    location = ParkingLocation.get_by_id(booking.parking_location_id)
                    if location:
                        location.available_slots += 1

        # Commit changes if any bookings were updated
        if expired_bookings:
            db.session.commit()

        return len(expired_bookings)

    def update_slot_details(self, slot_id, vehicle_type):
        """Update booking with slot details"""
        self.parking_slot_id = slot_id
        self.vehicle_type = vehicle_type

        # Adjust the total_price based on vehicle type
        if vehicle_type == "two-wheeler":
            # Apply 50% discount for two-wheelers
            self.total_price = round(self.total_price * 0.5)
        # No adjustment needed for four-wheelers as it's already at full price

        # Update the available slots count in the parking location
        from app.models.parking_location import ParkingLocation

        location = ParkingLocation.query.get(self.parking_location_id)
        if location and location.available_slots > 0:
            location.available_slots -= 1

        db.session.commit()
        return self

    def update_payment_details(self, payment_method, payment_status):
        """Update booking payment details"""
        self.payment_method = payment_method

        # If it's cash payment and confirmation page, set as paid
        if payment_method == "cash":
            self.payment_status = "paid"
        else:
            self.payment_status = payment_status

        self.booking_status = "confirmed"
        db.session.commit()
        return self

    def cancel_booking(self):
        """Cancel a booking."""
        self.booking_status = "cancelled"
        db.session.commit()
        return self

    def to_dict(self):
        """Convert the booking to a dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "parking_location_id": self.parking_location_id,
            "parking_slot_id": self.parking_slot_id,
            "vehicle_number": self.vehicle_number,
            "vehicle_type": self.vehicle_type,
            "booking_date": (
                self.booking_date.strftime("%Y-%m-%d") if self.booking_date else None
            ),
            "start_time": (
                self.start_time.strftime("%H:%M") if self.start_time else None
            ),
            "end_time": self.end_time.strftime("%H:%M") if self.end_time else None,
            "duration_hours": self.duration_hours,
            "total_price": self.total_price,
            "payment_method": self.payment_method,
            "payment_status": self.payment_status,
            "booking_status": self.booking_status,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
