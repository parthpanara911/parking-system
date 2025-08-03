from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app.models.user import User
from app.models.booking import Booking
from app.models.parking_location import ParkingLocation
from app.models.parking_slot import ParkingSlot
from app.extensions import db
import datetime

# Create admin blueprint
admin = Blueprint("admin", __name__, url_prefix="/admin")


# Admin only decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("You do not have permission to access this page.", "danger")
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)

    return decorated_function


# Context processor for admin blueprint to provide revenue data to all admin templates
@admin.context_processor
def admin_context():
    today = datetime.datetime.now().date()
    first_day_of_month = today.replace(day=1)
    first_day_of_year = today.replace(day=1, month=1)

    daily_revenue_result = (
        db.session.query(db.func.sum(Booking.total_price))
        .filter(db.func.date(Booking.created_at) == today)
        .filter(Booking.payment_status == "paid")
        .scalar()
    )
    daily_revenue = 0 if daily_revenue_result is None else daily_revenue_result

    monthly_revenue_result = (
        db.session.query(db.func.sum(Booking.total_price))
        .filter(db.func.date(Booking.created_at) >= first_day_of_month)
        .filter(Booking.payment_status == "paid")
        .scalar()
    )
    monthly_revenue = 0 if monthly_revenue_result is None else monthly_revenue_result
    
    yearly_revenue_result = (
        db.session.query(db.func.sum(Booking.total_price))
        .filter(db.func.date(Booking.created_at) >= first_day_of_year)
        .filter(Booking.payment_status == "paid")
        .scalar()
    )
    yearly_revenue = 0 if yearly_revenue_result is None else yearly_revenue_result

    return {"daily_revenue": daily_revenue, "monthly_revenue": monthly_revenue, "yearly_revenue": yearly_revenue}


@admin.route("/")
@login_required
@admin_required
def dashboard():
    """Admin dashboard homepage."""
    # Get basic statistics for the dashboard
    total_locations = ParkingLocation.query.count()
    total_slots = ParkingSlot.query.count()
    occupied_slots = ParkingSlot.query.filter_by(is_available=False).count()
    total_users = User.query.count()

    # Get recent parking activity (last 10 bookings)
    recent_bookings = Booking.query.order_by(Booking.created_at.desc()).filter(Booking.payment_status == "paid").limit(10).all()

    return render_template(
        "admin/index.html",
        total_locations=total_locations,
        total_slots=total_slots,
        occupied_slots=occupied_slots,
        total_users=total_users,
        recent_bookings=recent_bookings,
    )


@admin.route("/parking-slots")
@login_required
@admin_required
def parking_slots():
    """Admin view for managing parking slots."""
    slots = ParkingSlot.query.all()
    locations = ParkingLocation.query.all()
    return render_template("admin/parking_slots.html", slots=slots, locations=locations)


@admin.route("/parking-slots/<int:slot_id>", methods=["DELETE"])
@login_required
@admin_required
def delete_parking_slot(slot_id):
    """Delete a parking slot."""
    slot = ParkingSlot.query.get_or_404(slot_id)

    # Check if slot has any active bookings
    active_bookings = Booking.query.filter_by(
        parking_slot_id=slot_id, booking_status=["pending", "confirmed"]
    ).count()

    if active_bookings > 0:
        return (
            jsonify(
                {"success": False, "message": "Cannot delete slot with active bookings"}
            ),
            400,
        )

    try:
        db.session.delete(slot)
        db.session.commit()
        return jsonify(
            {"success": True, "message": "Parking slot deleted successfully"}
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


@admin.route("/users")
@login_required
@admin_required
def users():
    """Admin view for managing users."""
    users = User.query.all()
    return render_template("admin/users.html", users=users)


@admin.route("/users/<int:user_id>", methods=["DELETE"])
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user and their associated data."""
    user = User.query.get_or_404(user_id)

    # Prevent deleting current admin user
    if user.id == current_user.id:
        return (
            jsonify({"success": False, "message": "Cannot delete your own account"}),
            400,
        )

    try:
        # Delete all bookings associated with this user
        Booking.query.filter_by(user_id=user_id).delete()

        # Delete the user
        db.session.delete(user)
        db.session.commit()
        return jsonify({"success": True, "message": "User deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


@admin.route("/bookings")
@login_required
@admin_required
def bookings():
    """Admin view for all bookings."""
    bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    return render_template("admin/bookings.html", bookings=bookings)


@admin.route("/bookings/<int:booking_id>", methods=["DELETE"])
@login_required
@admin_required
def delete_booking(booking_id):
    """Delete a booking."""
    booking = Booking.query.get_or_404(booking_id)

    try:
        # If the booking has a slot and it's reserved, release it
        if booking.parking_slot_id and booking.booking_status in [
            "confirmed",
            "pending",
        ]:
            slot = ParkingSlot.query.get(booking.parking_slot_id)
            if slot and not slot.is_available:
                slot.is_available = True
                slot.is_reserved = False

                # Update available slots count in the parking location
                location = ParkingLocation.query.get(booking.parking_location_id)

        # Delete the booking
        db.session.delete(booking)
        db.session.commit()
        return jsonify({"success": True, "message": "Booking deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@admin.route("/booking-history")
@login_required
@admin_required
def booking_history():
    """Admin view for booking history."""
    completed_bookings = (
        Booking.query.filter(Booking.booking_status == "completed")
        .order_by(Booking.created_at.desc())
        .all()
    )
    return render_template("admin/booking_history.html", bookings=completed_bookings)


@admin.route("/vehicles")
@login_required
@admin_required
def vehicles():
    """Admin view for managing vehicles."""
    # Join user and vehicle data
    users = User.query.all()
    return render_template("admin/vehicles.html", users=users)


@admin.route("/payments")
@login_required
@admin_required
def payments():
    """Admin view for payment transactions."""
    bookings = (
        Booking.query.filter(Booking.payment_status == "paid")
        .order_by(Booking.created_at.desc())
        .all()
    )
    return render_template("admin/payments.html", bookings=bookings)
