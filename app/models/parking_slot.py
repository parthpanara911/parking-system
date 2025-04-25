from datetime import datetime
from app import db


class ParkingSlot(db.Model):
    __tablename__ = "parking_slots"

    id = db.Column(db.Integer, primary_key=True)
    parking_location_id = db.Column(
        db.Integer, db.ForeignKey("parking_locations.id"), nullable=False
    )
    vehicle_type = db.Column(
        db.String(20), nullable=False
    )  # "two-wheeler" or "four-wheeler"
    slot_number = db.Column(db.String(10), nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    is_reserved = db.Column(db.Boolean, default=False)
    hourly_rate = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Define relationship with ParkingLocation
    parking_location = db.relationship("ParkingLocation", backref="slots")

    def __repr__(self):
        return f"<ParkingSlot {self.slot_number} ({self.vehicle_type})>"

    @classmethod
    def get_available_slots(cls, parking_location_id, vehicle_type):
        """Get available parking slots by location and vehicle type."""
        return cls.query.filter_by(
            parking_location_id=parking_location_id,
            vehicle_type=vehicle_type,
            is_available=True,
        ).all()

    @classmethod
    def get_all_slots(cls, parking_location_id, vehicle_type):
        """Get all parking slots by location and vehicle type, both available and unavailable."""
        return cls.query.filter_by(
            parking_location_id=parking_location_id,
            vehicle_type=vehicle_type,
        ).all()

    @classmethod
    def get_by_id(cls, slot_id):
        """Get a parking slot by ID."""
        return cls.query.get(slot_id)

    @classmethod
    def reserve_slot(cls, slot_id):
        """Mark a slot as reserved (not available)."""
        slot = cls.get_by_id(slot_id)
        if slot and slot.is_available:
            slot.is_available = False
            slot.is_reserved = True
            db.session.commit()
            return True
        return False

    @classmethod
    def release_slot(cls, slot_id):
        """Mark a slot as available again."""
        slot = cls.get_by_id(slot_id)
        if slot and not slot.is_available:
            slot.is_available = True
            slot.is_reserved = False
            db.session.commit()
            return True
        return False

    def to_dict(self):
        """Convert the parking slot to a dictionary."""
        return {
            "id": self.id,
            "parking_location_id": self.parking_location_id,
            "vehicle_type": self.vehicle_type,
            "slot_number": self.slot_number,
            "is_available": self.is_available,
            "is_reserved": self.is_reserved,
            "hourly_rate": self.hourly_rate,
        }
