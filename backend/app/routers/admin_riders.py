from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.deps import get_current_admin
from app.models.user import User
from app.schemas.user import UserCreate, UserRead
from app.core.security import hash_password
from app.models.shift import Shift

router = APIRouter()

# ---------------------------
# GET - List Riders
# ---------------------------
@router.get("/", response_model=list[UserRead])
def list_riders(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    return db.query(User).filter(User.role == "rider").all()

# ---------------------------
# POST - Create Rider
# ---------------------------
@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_rider(
    data: UserCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    existing = db.query(User).filter(User.login_id == data.login_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="login_id already exists")

    if data.email:
        existing_email = db.query(User).filter(User.email == data.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="email already exists")

    rider = User(
        login_id=data.login_id,
        email=data.email,
        hashed_password=hash_password(data.password),
        role="rider"
    )

    db.add(rider)
    db.commit()
    db.refresh(rider)
    return rider

# ---------------------------
# GET - Single Rider
# ---------------------------
@router.get("/{rider_id}", response_model=UserRead)
def get_rider(
    rider_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    rider = db.query(User).filter(User.id == rider_id, User.role == "rider").first()
    if not rider:
        raise HTTPException(status_code=404, detail="Rider not found")
    return rider

# ---------------------------
# PUT - Update Rider
# ---------------------------
@router.put("/{rider_id}", response_model=UserRead)
def update_rider(
    rider_id: int,
    data: UserCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    rider = db.query(User).filter(User.id == rider_id, User.role == "rider").first()
    if not rider:
        raise HTTPException(status_code=404, detail="Rider not found")

    rider.login_id = data.login_id
    rider.email = data.email
    rider.hashed_password = hash_password(data.password)

    db.commit()
    db.refresh(rider)
    return rider

# ---------------------------
# DELETE - Remove Rider
# ---------------------------
@router.delete("/{rider_id}")
def delete_rider(
    rider_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    rider = db.query(User).filter(User.id == rider_id, User.role == "rider").first()
    if not rider:
        raise HTTPException(status_code=404, detail="Rider not found")

    db.delete(rider)
    db.commit()
    return {"message": "deleted"}

@router.get("/{rider_id}/payout")
def rider_payout(
    rider_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    rider = db.query(User).filter(User.id == rider_id).first()
    if not rider:
        raise HTTPException(status_code=404, detail="Rider not found")

    shifts = db.query(Shift).filter(
        Shift.rider_id == rider_id,
        Shift.status == "completed"
    ).all()

    total_hours = sum(s.hours_worked or 0 for s in shifts)
    rate = rider.hourly_rate or 0
    total_pay = round(total_hours * rate, 2)

    return {
        "rider_id": rider.id,
        "login_id": rider.login_id,
        "total_hours": total_hours,
        "hourly_rate": rate,
        "total_payment": total_pay
    }
