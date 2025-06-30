from datetime import datetime
from app import db
from app.models.parking_slot import ParkingSlot

class ParkingLocation(db.Model):
    __tablename__ = "parking_locations"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    area = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    total_slots = db.Column(db.Integer, nullable=False)
    available_slots = db.Column(db.Integer, nullable=False)
    hourly_rate = db.Column(db.Float, nullable=False)
    opening_time = db.Column(db.String(10), nullable=False)  
    closing_time = db.Column(db.String(10), nullable=False) 
    image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<ParkingLocation {self.name}>"

    @classmethod
    def get_all_locations(cls):
        """Get all parking locations."""
        return cls.query.all()

    @classmethod
    def get_by_id(cls, location_id):
        """Get a parking location by ID."""
        return cls.query.get(location_id)

    @classmethod
    def get_by_area(cls, area):
        """Get parking locations by area."""
        return cls.query.filter_by(area=area).all()

    @classmethod
    def get_by_city(cls, city):
        """Get parking locations by city."""
        return cls.query.filter_by(city=city).all()
    
    def update_available_slots(self):
        self.available_slots = ParkingSlot.query.filter_by(
            parking_location_id=self.id,
            is_available=True
        ).count()
        db.session.commit()

    def to_dict(self):
        """Convert the parking location to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "area": self.area,
            "city": self.city,
            "state": self.state,
            "pincode": self.pincode,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "total_slots": self.total_slots,
            "available_slots": self.available_slots,
            "hourly_rate": self.hourly_rate,
            "opening_time": self.opening_time,
            "closing_time": self.closing_time,
            "image_url": self.image_url,
        }
