from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.session import get_db
from app.core.deps import get_current_admin
from app.models.shift import Shift
from app.models.user import User
from app.schemas.payroll import MonthlyPayroll

# 🔧 FIX: REMOVED prefix from here
router = APIRouter(tags=["Payroll"])


@router.get("/", response_model=list[MonthlyPayroll])
def get_monthly_payroll(
    year: int = Query(..., example=2025),
    month: int = Query(..., example=1),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    start = datetime(year, month, 1)

    if month == 12:
        end = datetime(year + 1, 1, 1)
    else:
        end = datetime(year, month + 1, 1)

    shifts = (
        db.query(Shift)
        .join(User, Shift.rider_id == User.id)
        .filter(
            Shift.status == "completed",
            Shift.start_time >= start,
            Shift.start_time < end,
        )
        .all()
    )

    payroll_map = {}

    for shift in shifts:
        if not shift.rider_id or not shift.end_time:
            continue

        hours = (shift.end_time - shift.start_time).total_seconds() / 3600
        rider = shift.rider

        if rider.hourly_rate is None:
            continue

        if rider.id not in payroll_map:
            payroll_map[rider.id] = {
                "rider_id": rider.id,
                "login_id": rider.login_id,
                "year": year,
                "month": month,
                "total_hours": 0.0,
                "hourly_rate": rider.hourly_rate,
                "payout": 0.0,
            }

        payroll_map[rider.id]["total_hours"] += hours
        payroll_map[rider.id]["payout"] += hours * rider.hourly_rate

    return list(payroll_map.values())
