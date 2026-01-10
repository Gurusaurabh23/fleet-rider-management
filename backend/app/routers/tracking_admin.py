from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date

from app.db.session import get_db
from app.core.deps import get_current_admin
from app.models.daily_distance import DailyDistance

router = APIRouter()

@router.get("/daily/{rider_id}")
def rider_daily_distance(
    rider_id: int,
    day: date,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    rec = db.query(DailyDistance).filter_by(rider_id=rider_id, date=day).first()
    if not rec:
        return {"rider_id": rider_id, "date": day, "distance": 0}
    return {"rider_id": rider_id, "date": day, "distance": rec.distance_km}
