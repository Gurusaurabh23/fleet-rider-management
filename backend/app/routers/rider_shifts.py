from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.session import get_db
from app.core.deps import get_current_rider
from app.models.shift import Shift
from app.models.user import User
from app.schemas.shift import ShiftRead

router = APIRouter(prefix="/riders/me/shifts", tags=["Rider - Shifts"])


@router.put("/shifts/{shift_id}/start")
def rider_start(shift_id: int, db: Session = Depends(get_db), rider=Depends(get_current_rider)):
    shift = db.query(Shift).filter(Shift.id == shift_id, Shift.rider_id == rider.id).first()
    if not shift:
        raise HTTPException(404, "Shift not found")
    shift.status = "active"
    shift.start_time = datetime.utcnow()
    db.commit()
    db.refresh(shift)
    return shift



@router.put("/shifts/{shift_id}/end")
def rider_end(shift_id: int, db: Session = Depends(get_db), rider=Depends(get_current_rider)):
    shift = db.query(Shift).filter(Shift.id == shift_id, Shift.rider_id == rider.id).first()
    if not shift:
        raise HTTPException(404, "Shift not found")

    shift.end_time = datetime.utcnow()
    shift.status = "completed"
    if shift.start_time:
        diff_hours = (shift.end_time - shift.start_time).total_seconds() / 3600
        shift.hours_worked = round(diff_hours, 2)

    db.commit()
    db.refresh(shift)
    return shift



@router.get("/", response_model=list[ShiftRead])
def my_shifts(
    db: Session = Depends(get_db),
    rider: User = Depends(get_current_rider)
):
    return db.query(Shift).filter(Shift.rider_id == rider.id).all()
