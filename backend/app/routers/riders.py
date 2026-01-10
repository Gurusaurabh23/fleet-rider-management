from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime, timedelta

from app.db.session import get_db
from app.core.deps import get_current_admin
from app.models.shift import Shift
from app.models.user import User
from app.models.gps import GPSLocation
from app.models.rider_weekly_orders import RiderWeeklyOrders
from app.routers.tracking import compute


router = APIRouter()


@router.get("/ping")
def ping():
    return {"message": "Riders router OK"}


# ---------------------------
# 🚀 Leaderboard by ORDERS (ADMIN)
# ---------------------------
# ---------------------------
# 🚀 Leaderboard by ORDERS (ADMIN – ENRICHED)
# ---------------------------
@router.get("/leaderboard")
def riders_leaderboard(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    week_start = date.today() - timedelta(days=date.today().weekday())

    results = (
        db.query(
            User.id.label("rider_id"),
            User.login_id,
            RiderWeeklyOrders.completed_orders
        )
        .join(RiderWeeklyOrders, RiderWeeklyOrders.rider_id == User.id)
        .filter(RiderWeeklyOrders.week_start == week_start)
        .order_by(RiderWeeklyOrders.completed_orders.desc())
        .all()
    )

    leaderboard = []

    for r in results:
        orders = r.completed_orders or 0

        # 🏅 Tier + Bonus + Status
        if orders >= 80:
            tier = "GOLD"
            weekly_bonus = 50
            status = "STAR"
        elif orders >= 40:
            tier = "SILVER"
            weekly_bonus = 20
            status = "ON_TRACK"
        else:
            tier = "BRONZE"
            weekly_bonus = 0
            status = "NEEDS_PUSH"

        leaderboard.append({
            "rider_id": r.rider_id,
            "login_id": r.login_id,
            "completed_orders": orders,
            "tier": tier,
            "weekly_bonus": weekly_bonus,
            "status": status,
        })

    return {
        "week_start": str(week_start),
        "count": len(leaderboard),
        "leaderboard": leaderboard,
    }



# ---------------------------
# 📅 Attendance Today (UNCHANGED)
# ---------------------------
@router.get("/attendance/today")
def attendance_today(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_end = datetime.combine(date.today(), datetime.max.time())

    results = (
        db.query(
            User.id.label("rider_id"),
            User.login_id,
            func.count(Shift.id).label("shift_count"),
            func.sum(Shift.hours_worked).label("total_hours")
        )
        .join(Shift, Shift.rider_id == User.id, isouter=True)
        .filter(Shift.start_time >= today_start, Shift.start_time <= today_end)
        .group_by(User.id)
        .order_by(func.sum(Shift.hours_worked).desc())
        .all()
    )

    attendance = []
    for r in results:
        total_hours = float(r.total_hours) if r.total_hours else 0.0
        status = "Absent"
        if total_hours >= 8:
            status = "Present"
        elif 0 < total_hours < 8:
            status = "Partial"

        attendance.append({
            "rider_id": r.rider_id,
            "login_id": r.login_id,
            "shift_count": r.shift_count,
            "total_hours": total_hours,
            "status": status
        })

    return {"date": str(date.today()), "attendance": attendance}


# ---------------------------
# 📊 Attendance Weekly (UNCHANGED)
# ---------------------------
@router.get("/attendance/weekly")
def attendance_weekly(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    start = datetime.now() - timedelta(days=7)

    results = (
        db.query(
            User.id.label("rider_id"),
            User.login_id,
            func.sum(Shift.hours_worked).label("hours_week")
        )
        .join(Shift, Shift.rider_id == User.id)
        .filter(Shift.start_time >= start)
        .group_by(User.id)
        .order_by(func.sum(Shift.hours_worked).desc())
        .all()
    )

    data = [
        {
            "rider_id": r.rider_id,
            "login_id": r.login_id,
            "hours_week": float(r.hours_week) if r.hours_week else 0.0
        }
        for r in results
    ]
    return {"start": str(start.date()), "end": str(date.today()), "weekly": data}


# ------------------------------------------------
# 🆕 RIDER STATS (ORDERS + RANKING – FINAL)
# ------------------------------------------------
@router.get("/stats/{login_id}")
def rider_stats_by_login_id(
    login_id: str,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.login_id == login_id).first()
    if not user:
        return {"error": "Rider not found"}

    week_start = date.today() - timedelta(days=date.today().weekday())

    record = (
        db.query(RiderWeeklyOrders)
        .filter(
            RiderWeeklyOrders.rider_id == user.id,
            RiderWeeklyOrders.week_start == week_start
        )
        .first()
    )

    week_orders = record.completed_orders if record else 0

    # -----------------------
    # 🏆 RANKING (NEW)
    # -----------------------
    all_riders = (
        db.query(RiderWeeklyOrders)
        .filter(RiderWeeklyOrders.week_start == week_start)
        .order_by(RiderWeeklyOrders.completed_orders.desc())
        .all()
    )

    rank = None
    total_riders = len(all_riders)

    for idx, r in enumerate(all_riders, start=1):
        if r.rider_id == user.id:
            rank = idx
            break

    # -----------------------
    # 🏅 TIERS (ORDERS-BASED)
    # -----------------------
    if week_orders >= 80:
        tier = "GOLD"
        next_tier = None
        orders_to_next = 0
        progress_percent = 100
        weekly_bonus_amount = 50
    elif week_orders >= 40:
        tier = "SILVER"
        next_tier = "GOLD"
        orders_to_next = 80 - week_orders
        progress_percent = int((week_orders / 80) * 100)
        weekly_bonus_amount = 20
    else:
        tier = "BRONZE"
        next_tier = "SILVER"
        orders_to_next = 40 - week_orders
        progress_percent = int((week_orders / 40) * 100)
        weekly_bonus_amount = 0

    return {
        "login_id": login_id,
        "week_orders": week_orders,
        "tier": tier,
        "next_tier": next_tier,
        "orders_to_next_tier": max(0, orders_to_next),
        "progress_percent": progress_percent,
        "weekly_bonus_amount": weekly_bonus_amount,
        "weekly_target_completed": week_orders >= 40,

        # 🆕 RANK INFO
        "rank": rank,
        "total_riders": total_riders,
    }
