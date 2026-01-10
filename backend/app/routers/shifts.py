from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.db.session import get_db
from app.core.deps import get_current_admin
from app.models.shift import Shift
from app.models.user import User
from app.schemas.shift import ShiftCreate, ShiftRead

router = APIRouter(prefix="/admin/shifts", tags=["Admin - Shifts"])


@router.post("/", response_model=ShiftRead)
def create_shift(
    shift: ShiftCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    rider = db.query(User).filter(User.id == shift.rider_id, User.role == "rider").first()
    if not rider:
        raise HTTPException(status_code=404, detail="Rider not found")

    # Create shift
    db_shift = Shift(
        rider_id=shift.rider_id,
        start_time=shift.start_time,
        end_time=shift.end_time,
    )
    db.add(db_shift)
    db.commit()
    db.refresh(db_shift)
    return db_shift


@router.get("/", response_model=List[ShiftRead])
def list_shifts(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    return db.query(Shift).all()


@router.get("/rider/{rider_id}", response_model=List[ShiftRead])
def get_rider_shifts(
    rider_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    return db.query(Shift).filter(Shift.rider_id == rider_id).all()
