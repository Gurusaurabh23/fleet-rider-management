from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from datetime import datetime, timedelta

from app.core.deps import get_current_rider
from app.models.user import User
from app.models.shift import ShiftBooking
from app.models.gps import GPSLocation
from app.db.session import get_db
from app.routers.tracking import compute

router = APIRouter()


@router.get("/me")
def rider_me(
    current_rider: User = Depends(get_current_rider),
    db: Session = Depends(get_db)
):
    return {
        "id": current_rider.id,
        "login_id": current_rider.login_id,
        "email": current_rider.email,
        "role": current_rider.role,
        "is_active": current_rider.is_active
    }


# -------------------------------
# 🆕 RIDER STATS (IMPORTANT)
# -------------------------------
@router.get("/me/stats")
def rider_stats(
    current_rider: User = Depends(get_current_rider),
    db: Session = Depends(get_db)
):
    now = datetime.utcnow()
    start_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_week = now - timedelta(days=7)

    # -----------------------
    # WORKED HOURS
    # -----------------------
    today_hours = (
        db.query(func.sum(ShiftBooking.worked_hours))
        .filter(
            ShiftBooking.rider_id == current_rider.id,
            ShiftBooking.date >= start_day.date(),
            ShiftBooking.attendance_status != "NO_SHOW",
        )
        .scalar()
    ) or 0

    week_hours = (
        db.query(func.sum(ShiftBooking.worked_hours))
        .filter(
            ShiftBooking.rider_id == current_rider.id,
            ShiftBooking.date >= start_week.date(),
            ShiftBooking.attendance_status != "NO_SHOW",
        )
        .scalar()
    ) or 0

    # -----------------------
    # WEEK DISTANCE
    # -----------------------
    gps_points = (
        db.query(GPSLocation)
        .filter(
            GPSLocation.rider_id == current_rider.id,
            GPSLocation.timestamp >= start_week,
        )
        .all()
    )

    week_km = compute(gps_points) if gps_points else 0

    # -----------------------
    # PERFORMANCE TIER
    # -----------------------
    tier = "BRONZE"
    if week_hours >= 40:
        tier = "GOLD"
    elif week_hours >= 25:
        tier = "SILVER"

    return {
        "today_hours": round(today_hours, 2),
        "week_hours": round(week_hours, 2),
        "week_km": round(week_km, 2),
        "tier": tier,
    }
