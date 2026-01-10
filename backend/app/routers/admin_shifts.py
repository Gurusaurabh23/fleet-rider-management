from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.session import get_db
from app.core.deps import get_current_admin
from app.models.shift import Shift
from app.models.user import User
from app.schemas.shift import ShiftRead
from typing import List

router = APIRouter()


from datetime import datetime, timedelta

@router.post("/")
def create_shift(
    start_time: datetime,
    duration_hours: float = 4,   # default duration = 4 hours
    db: Session = Depends(get_db)
):
    # Create new shift
    new_shift = Shift(
        start_time=start_time,
        end_time=start_time + timedelta(hours=duration_hours),
        duration_hours=duration_hours,
        status="scheduled"
    )

    db.add(new_shift)
    db.commit()
    db.refresh(new_shift)
    return new_shift


@router.get("/", response_model=List[ShiftRead])
def list_shifts(db: Session = Depends(get_db)):
    shifts = db.query(Shift).all()
    return shifts


@router.put("/{shift_id}/assign/{rider_id}")
def assign_rider(shift_id: int, rider_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):

    shift = db.query(Shift).filter(Shift.id == shift_id).first()
    rider = db.query(User).filter(User.id == rider_id, User.role == "rider").first()

    if not shift:
        raise HTTPException(404, "Shift not found")

    if not rider:
        raise HTTPException(404, "Rider not found")

    if rider.hourly_rate is None:
        raise HTTPException(400, "Rider has no hourly_rate set")

    shift.rider_id = rider_id
    shift.status = "active"
    shift.hourly_rate = rider.hourly_rate   # ⭐️ FIX

    db.commit()
    db.refresh(shift)
    return shift

    return shift


@router.put("/{shift_id}/close", response_model=ShiftRead)
def close_shift(shift_id: int, db: Session = Depends(get_db)):
    shift = db.query(Shift).filter(Shift.id == shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")

    if shift.status == "completed":
        raise HTTPException(status_code=400, detail="Shift already closed")

    # Must have assigned rider
    if not shift.rider_id:
        raise HTTPException(status_code=400, detail="Assign rider first")

    # Must have a start time
    if not shift.start_time:
        raise HTTPException(status_code=400, detail="Start time missing")

    # Compute closing values
    shift.end_time = datetime.utcnow()
    diff = shift.end_time - shift.start_time
    hours = diff.total_seconds() / 3600
    shift.hours_worked = round(hours, 2)

    # Get rider hourly_rate
    rider = db.query(User).filter(User.id == shift.rider_id).first()
    hr = rider.hourly_rate or 0.0
    shift.hourly_rate = hr
    shift.payout = round(shift.hours_worked * hr, 2)

    shift.status = "completed"
    db.commit()
    db.refresh(shift)
    return shift








@router.delete("/{shift_id}")
def delete_shift(
    shift_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Admin deletes a shift"""
    shift = db.query(Shift).filter(Shift.id == shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")

    db.delete(shift)
    db.commit()
    return {"deleted": shift_id}
