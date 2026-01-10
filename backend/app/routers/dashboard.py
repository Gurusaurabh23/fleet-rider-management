from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from datetime import datetime, timedelta

from app.db.session import get_db
from app.core.deps import get_current_admin
from app.models.user import User
from app.models.gps import GPSLocation
from app.models.payroll import Payroll
from app.models.bonus import Bonus
from app.models.shift import ShiftBooking
from app.routers.tracking import compute

router = APIRouter()


# -------------------------------
# HELPER: WEEKLY BONUS GENERATION
# -------------------------------
def generate_weekly_bonus(db: Session, rider_id, week_start, week_end):
    total_hours = (
        db.query(func.sum(ShiftBooking.worked_hours))
        .filter(
            ShiftBooking.rider_id == rider_id,
            ShiftBooking.date >= week_start,
            ShiftBooking.date <= week_end,
            ShiftBooking.attendance_status != "NO_SHOW",
        )
        .scalar()
    ) or 0

    bonus_amount = Bonus.calculate_weekly_bonus(total_hours)

    if bonus_amount == 0:
        return

    # prevent duplicate weekly bonus
    existing = (
        db.query(Bonus)
        .filter(
            Bonus.rider_id == rider_id,
            Bonus.week_start == week_start,
        )
        .first()
    )

    if existing:
        return

    bonus = Bonus(
        rider_id=rider_id,
        week_start=week_start,
        amount=bonus_amount,
    )

    db.add(bonus)
    db.commit()


# -------------------------------
# HELPER: WEEKLY PERFORMANCE TIER
# -------------------------------
def calculate_weekly_tier(db: Session, rider_id, week_start, week_end):
    total_hours = (
        db.query(func.sum(ShiftBooking.worked_hours))
        .filter(
            ShiftBooking.rider_id == rider_id,
            ShiftBooking.date >= week_start,
            ShiftBooking.date <= week_end,
            ShiftBooking.attendance_status != "NO_SHOW",
        )
        .scalar()
    ) or 0

    no_show_count = (
        db.query(ShiftBooking)
        .filter(
            ShiftBooking.rider_id == rider_id,
            ShiftBooking.date >= week_start,
            ShiftBooking.date <= week_end,
            ShiftBooking.attendance_status == "NO_SHOW",
        )
        .count()
    )

    return Bonus.calculate_weekly_tier(
        total_hours=total_hours,
        no_show_count=no_show_count,
    )


@router.get("/summary")
def dashboard_summary(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    now = datetime.utcnow()
    start_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_week = now - timedelta(days=7)

    # counts
    total_riders = db.query(User).filter(User.role=="rider").count()
    active_riders = db.query(User).filter(User.role=="rider", User.is_active==True).count()

    # distance day
    day_points = db.query(GPSLocation).filter(GPSLocation.timestamp >= start_day).all()
    week_points = db.query(GPSLocation).filter(GPSLocation.timestamp >= start_week).all()

    # compute totals across all riders
    def total_distance(points):
        return compute(points)

    total_km_day = total_distance(day_points)
    total_km_week = total_distance(week_points)

    # payroll summary
    payroll_day = db.query(Payroll).filter(Payroll.generated_at >= start_day).all()
    payroll_week = db.query(Payroll).filter(Payroll.generated_at >= start_week).all()

    total_pay_day = sum(p.amount for p in payroll_day)
    total_pay_week = sum(p.amount for p in payroll_week)

    # Top 5 by distance this week
    # We reuse distance logic by grouping
    weekly_report = {}
    for p in week_points:
        weekly_report.setdefault(p.rider_id, []).append(p)

    leaderboard = []
    for rider_id, pts in weekly_report.items():
        km = compute(pts)
        rider = db.query(User).filter(User.id==rider_id).first()

        # ✅ NEW: calculate weekly tier
        tier = calculate_weekly_tier(
            db=db,
            rider_id=rider_id,
            week_start=start_week.date(),
            week_end=now.date(),
        )

        leaderboard.append({
            "rider_id": rider_id,
            "login_id": rider.login_id,
            "km": km,
            "tier": tier
        })

        # ✅ existing: generate weekly bonus
        generate_weekly_bonus(
            db=db,
            rider_id=rider_id,
            week_start=start_week.date(),
            week_end=now.date(),
        )

    leaderboard.sort(key=lambda x: x["km"], reverse=True)
    leaderboard = leaderboard[:5]

    return {
        "total_riders": total_riders,
        "active_riders": active_riders,
        "km_today": total_km_day,
        "km_week": total_km_week,
        "pay_today": round(total_pay_day, 2),
        "pay_week": round(total_pay_week, 2),
        "leaderboard": leaderboard,
        "timestamp": now
    }

@router.get("/analytics/riders")
def rider_analytics(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    now = datetime.utcnow()
    start_week = now - timedelta(days=7)

    riders = db.query(User).filter(User.role == "rider").all()

    analytics = []

    for rider in riders:
        total_hours = (
            db.query(func.sum(ShiftBooking.worked_hours))
            .filter(
                ShiftBooking.rider_id == rider.id,
                ShiftBooking.date >= start_week.date(),
                ShiftBooking.attendance_status != "NO_SHOW",
            )
            .scalar()
        ) or 0

        total_pay = (
            db.query(func.sum(Payroll.amount))
            .filter(
                Payroll.rider_id == rider.id,
                Payroll.generated_at >= start_week,
            )
            .scalar()
        ) or 0

        gps_points = (
            db.query(GPSLocation)
            .filter(
                GPSLocation.rider_id == rider.id,
                GPSLocation.timestamp >= start_week,
            )
            .all()
        )

        total_km = compute(gps_points)

        km_per_hour = round(total_km / total_hours, 2) if total_hours > 0 else 0

        no_shows = (
            db.query(ShiftBooking)
            .filter(
                ShiftBooking.rider_id == rider.id,
                ShiftBooking.date >= start_week.date(),
                ShiftBooking.attendance_status == "NO_SHOW",
            )
            .count()
        )

        analytics.append({
            "rider_id": rider.id,
            "login_id": rider.login_id,
            "hours": round(total_hours, 2),
            "pay": round(total_pay, 2),
            "km": round(total_km, 2),
            "km_per_hour": km_per_hour,
            "no_shows": no_shows,
        })

    return {
        "week_start": start_week.date(),
        "data": analytics
    }
