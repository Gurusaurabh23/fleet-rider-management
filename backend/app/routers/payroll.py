from fastapi import APIRouter

router = APIRouter()
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from sqlalchemy import func

from app.db.session import get_db
from app.core.deps import get_current_admin
from app.models.shift import Shift
from app.models.payroll import Payroll

router = APIRouter(prefix="/admin/payroll", tags=["Admin - Payroll"])


@router.post("/generate/{rider_id}/{day}")
def generate_payroll(
    rider_id: int,
    day: str,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    work_day = date.fromisoformat(day)

    # get closed shifts
    shifts = db.query(Shift).filter(
        Shift.rider_id == rider_id,
        func.date(Shift.start_time) == work_day,
        Shift.end_time.isnot(None)
    ).all()

    if not shifts:
        raise HTTPException(404, "No completed shifts found")

    total_hours = 0
    for s in shifts:
        seconds = (s.end_time - s.start_time).total_seconds()
        total_hours += seconds / 3600

    amount = round(total_hours * 13, 2)

    record = Payroll(
        rider_id=rider_id,
        date=work_day,
        total_hours=round(total_hours, 2),
        amount=amount
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "message": "Payroll generated",
        "total_hours": record.total_hours,
        "amount": record.amount
    }

@router.get("/{day}")
def payroll_report(
    day: str,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    work_day = date.fromisoformat(day)

    records = db.query(Payroll).filter(
        Payroll.date == work_day
    ).all()

    return records
