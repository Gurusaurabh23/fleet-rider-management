# backend/app/services/shift_service.py

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.shift import ShiftBooking
from app.models.shift import ShiftTemplate
from app.models.gps import GpsLocation
from app.models.redzone import RedZone
from app.models.notifications import Notification
from app.routers.tracking import compute


MIN_PARTIAL_HOURS = 2
IDLE_MINUTES = 10
NOTIFICATION_COOLDOWN_MINUTES = 30

# abuse protection
MAX_KM_PER_HOUR = 40
MIN_KM_PER_HOUR = 1.5


def is_gps_data_valid(gps_points):
    if len(gps_points) < 2:
        return True

    total_distance = compute(gps_points)
    total_time_hours = (
        (gps_points[-1].timestamp - gps_points[0].timestamp).total_seconds() / 3600
    )

    if total_time_hours <= 0:
        return False

    speed = total_distance / total_time_hours
    return speed <= MAX_KM_PER_HOUR


def calculate_shift_metrics(db: Session, booking_id):
    """
    Calculates:
    - actual_start_time
    - actual_end_time
    - worked_hours
    - attendance_status

    Also:
    - checks zone & idle state
    - sends smart notification if needed

    Called:
    - when a shift is completed
    - or before payroll is generated
    """

    booking = (
        db.query(ShiftBooking)
        .filter(ShiftBooking.id == booking_id)
        .first()
    )

    if not booking:
        return

    shift = (
        db.query(ShiftTemplate)
        .filter(ShiftTemplate.id == booking.shift_template_id)
        .first()
    )

    if not shift:
        return

    # Fetch GPS points during shift window
    gps_points = (
        db.query(GpsLocation)
        .filter(
            GpsLocation.rider_id == booking.rider_id,
            GpsLocation.timestamp >= shift.start_time,
            GpsLocation.timestamp <= shift.end_time,
        )
        .order_by(GpsLocation.timestamp.asc())
        .all()
    )

    # -------------------------
    # NO SHOW
    # -------------------------
    if not gps_points:
        booking.actual_start_time = None
        booking.actual_end_time = None
        booking.worked_hours = 0
        booking.attendance_status = "NO_SHOW"

        db.commit()
        return

    # -------------------------
    # GPS VALIDATION (NEW)
    # -------------------------
    if not is_gps_data_valid(gps_points):
        booking.actual_start_time = None
        booking.actual_end_time = None
        booking.worked_hours = 0
        booking.attendance_status = "INVALID_GPS"

        db.commit()
        return

    # -------------------------
    # ACTUAL TIMES
    # -------------------------
    actual_start = gps_points[0].timestamp
    actual_end = gps_points[-1].timestamp

    worked_hours = max(
    0,
    round((actual_end - actual_start).total_seconds() / 3600, 2)
   
    )

    worked_hours = round(worked_hours, 2)

    booking.actual_start_time = actual_start
    booking.actual_end_time = actual_end
    booking.worked_hours = worked_hours

    # -------------------------
    # ATTENDANCE STATUS
    # -------------------------
    attendance_status = "PRESENT"

    if worked_hours < MIN_PARTIAL_HOURS:
        attendance_status = "PARTIAL"
    elif actual_start > shift.start_time:
        attendance_status = "LATE"
    elif actual_end < shift.end_time:
        attendance_status = "LEFT_EARLY"

    # -------------------------
    # LOW PRODUCTIVITY CHECK (NEW)
    # -------------------------
    total_km = compute(gps_points)
    km_per_hour = total_km / worked_hours if worked_hours > 0 else 0

    if km_per_hour < MIN_KM_PER_HOUR:
        attendance_status = "LOW_PRODUCTIVITY"

    booking.attendance_status = attendance_status

    db.commit()

    # -------------------------
    # ZONE & IDLE CHECK
    # -------------------------
    check_zone_and_notify(db, booking.rider_id)


def check_zone_and_notify(db: Session, rider_id):
    """
    Sends smart notification if:
    - rider is idle
    - or outside red zone
    """

    last_gps = (
        db.query(GpsLocation)
        .filter(GpsLocation.rider_id == rider_id)
        .order_by(desc(GpsLocation.timestamp))
        .first()
    )

    if not last_gps:
        return

    now = datetime.utcnow()

    # Idle check
    if last_gps.timestamp < now - timedelta(minutes=IDLE_MINUTES):
        message = "You are idle. Move towards a high-demand zone to get more orders."
    else:
        # Check if inside active red zone
        red_zones = db.query(RedZone).filter(RedZone.active == True).all()

        inside_red_zone = False
        for zone in red_zones:
            if zone.contains(last_gps.latitude, last_gps.longitude):
                inside_red_zone = True
                break

        if inside_red_zone:
            return

        message = "High demand nearby. Move towards a red zone to increase orders."

    # Notification cooldown
    recent_notification = (
        db.query(Notification)
        .filter(
            Notification.rider_id == rider_id,
            Notification.created_at >= now - timedelta(minutes=NOTIFICATION_COOLDOWN_MINUTES),
        )
        .first()
    )

    if recent_notification:
        return

    notification = Notification(
        rider_id=rider_id,
        message=message,
        type="ZONE_NUDGE",
    )

    db.add(notification)
    db.commit()
