from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta
import csv
import io

from app.db.session import get_db
from app.core.deps import get_current_admin
from app.models.user import User
from app.models.shift import Shift
from app.models.rider_weekly_orders import RiderWeeklyOrders

router = APIRouter()


@router.get("/stats")
def dashboard_stats(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    """Admin dashboard summary numbers"""

    total_riders = db.query(User).filter(User.role == "rider").count()
    active_riders = db.query(User).filter(User.role == "rider", User.is_active == True).count()

    total_shifts = db.query(Shift).count()
    active_shifts = db.query(Shift).filter(Shift.status == "active").count()
    completed_shifts = db.query(Shift).filter(Shift.status == "completed").count()

    return {
        "total_riders": total_riders,
        "active_riders": active_riders,
        "total_shifts": total_shifts,
        "active_shifts": active_shifts,
        "completed_shifts": completed_shifts
    }


@router.get("/weekly-impact")
def weekly_impact_summary(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    week_start = date.today() - timedelta(days=date.today().weekday())

    records = (
        db.query(
            User.login_id,
            RiderWeeklyOrders.completed_orders
        )
        .join(RiderWeeklyOrders, RiderWeeklyOrders.rider_id == User.id)
        .filter(RiderWeeklyOrders.week_start == week_start)
        .all()
    )

    total_orders = sum(r.completed_orders for r in records)
    active_riders = len(records)

    total_bonus = 0
    top_rider = None
    max_orders = 0

    for r in records:
        orders = r.completed_orders

        if orders >= 80:
            total_bonus += 50
        elif orders >= 40:
            total_bonus += 20

        if orders > max_orders:
            max_orders = orders
            top_rider = r.login_id

    return {
        "week_start": str(week_start),
        "total_orders": total_orders,
        "active_riders": active_riders,
        "total_bonus": total_bonus,
        "top_rider": top_rider,
    }

# ------------------------------------------------
# 🆕 UBER EATS WEEKLY CSV UPLOAD (ADMIN)
# ------------------------------------------------
@router.post("/uber-orders/upload")
def upload_uber_orders_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    content = file.file.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))

    if "login_id" not in reader.fieldnames or "completed_orders" not in reader.fieldnames:
        raise HTTPException(
            status_code=400,
            detail="CSV must contain 'login_id' and 'completed_orders' columns",
        )

    # Calculate week start (Monday)
    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    processed = 0
    skipped = 0
    errors = []

    for row in reader:
        login_id = row.get("login_id")
        orders_raw = row.get("completed_orders")

        if not login_id or not orders_raw:
            skipped += 1
            continue

        try:
            completed_orders = int(orders_raw)
        except ValueError:
            errors.append(f"Invalid order count for {login_id}")
            continue

        user = (
            db.query(User)
            .filter(User.login_id == login_id, User.role == "rider")
            .first()
        )

        if not user:
            errors.append(f"Rider not found: {login_id}")
            continue

        existing = (
            db.query(RiderWeeklyOrders)
            .filter(
                RiderWeeklyOrders.rider_id == user.id,
                RiderWeeklyOrders.week_start == week_start,
            )
            .first()
        )

        if existing:
            existing.completed_orders = completed_orders
        else:
            record = RiderWeeklyOrders(
                rider_id=user.id,
                week_start=week_start,
                completed_orders=completed_orders,
            )
            db.add(record)

        processed += 1

    db.commit()

    return {
        "week_start": str(week_start),
        "processed": processed,
        "skipped": skipped,
        "errors": errors,
    }
