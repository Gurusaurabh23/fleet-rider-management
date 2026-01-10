from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from app.db.session import get_db
from app.core.deps import get_current_rider, get_current_admin
from app.schemas.gps import GPSCreate, GPSRead
from app.models.gps import GPSLocation
from app.models.user import User
from app.models.notifications import MovementNotification
from app.utils.gps import haversine  # for distance calc


router = APIRouter()

# CONFIG
MIN_UPDATE_SECONDS = 30            # rider must wait 30s between updates
STAGNANT_MINUTES = 8               # alert if standing still 8 min
STAGNANT_DISTANCE_METERS = 30      # consider “no movement” if < 30 m


# ------------------------------------
# 1. Rider GPS update
# ------------------------------------
@router.post("/update", response_model=GPSRead)
def update_location(
    data: GPSCreate,
    db: Session = Depends(get_db),
    rider: User = Depends(get_current_rider)
):
    now = datetime.utcnow()

    # previous position
    last = (
        db.query(GPSLocation)
        .filter(GPSLocation.rider_id == rider.id)
        .order_by(GPSLocation.timestamp.desc())
        .first()
    )

    # enforce 30 sec rule
    if last and last.timestamp > now - timedelta(seconds=MIN_UPDATE_SECONDS):
        raise HTTPException(
            status_code=400,
            detail=f"Wait {MIN_UPDATE_SECONDS}s before next GPS update"
        )

    # store new point
    new_point = GPSLocation(
        rider_id=rider.id,
        latitude=data.latitude,
        longitude=data.longitude,
    )
    db.add(new_point)
    db.commit()
    db.refresh(new_point)

    # No stagnation check if it’s the first point
    if not last:
        return new_point

    # compute small movement
    meters = haversine(
        last.latitude, last.longitude,
        new_point.latitude, new_point.longitude
    ) * 1000  # convert km → meters

    mins_stopped = (now - last.timestamp).total_seconds() / 60

    # check stagnation rule
    if meters < STAGNANT_DISTANCE_METERS and mins_stopped >= STAGNANT_MINUTES:
        notif = MovementNotification(
            rider_id=rider.id,
            last_lat=new_point.latitude,
            last_lng=new_point.longitude,
            minutes_stopped=int(mins_stopped),
            message="You are stationary too long — move to active area!"
        )
        db.add(notif)
        db.commit()

    return new_point


# ------------------------------------
# 2. ADMIN: Latest rider location
# ------------------------------------
@router.get("/latest/{rider_id}", response_model=GPSRead)
def get_latest_location(
    rider_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    loc = (
        db.query(GPSLocation)
        .filter(GPSLocation.rider_id == rider_id)
        .order_by(GPSLocation.timestamp.desc())
        .first()
    )
    if not loc:
        raise HTTPException(status_code=404, detail="No GPS data found")
    return loc


# ------------------------------------
# 3. ADMIN: Rider GPS history
# ------------------------------------
@router.get("/history/{rider_id}", response_model=List[GPSRead])
def get_history(
    rider_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    return (
        db.query(GPSLocation)
        .filter(GPSLocation.rider_id == rider_id)
        .order_by(GPSLocation.timestamp.desc())
        .all()
    )


# ------------------------------------
# 4. Rider — Distance Today
# ------------------------------------
@router.get("/distance/today")
def distance_today(
    db: Session = Depends(get_db),
    rider: User = Depends(get_current_rider)
):
    today = datetime.utcnow().date()
    points = (
        db.query(GPSLocation)
        .filter(GPSLocation.rider_id == rider.id)
        .filter(GPSLocation.timestamp >= today)
        .order_by(GPSLocation.timestamp)
        .all()
    )
    return {"km_today": compute(points)}


# ------------------------------------
# 5. Rider — Distance Reports
# ------------------------------------
@router.get("/me/distance/today")
def rider_distance_today(
    rider=Depends(get_current_rider),
    db: Session = Depends(get_db)
):
    start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    pts = (
        db.query(GPSLocation)
        .filter(GPSLocation.rider_id == rider.id, GPSLocation.timestamp >= start)
        .order_by(GPSLocation.timestamp)
        .all()
    )
    return {"date": start.date(), "km": compute(pts)}


@router.get("/me/distance/week")
def rider_distance_week(
    rider=Depends(get_current_rider),
    db: Session = Depends(get_db)
):
    start = datetime.utcnow() - timedelta(days=7)
    pts = (
        db.query(GPSLocation)
        .filter(GPSLocation.rider_id == rider.id, GPSLocation.timestamp >= start)
        .order_by(GPSLocation.timestamp)
        .all()
    )
    return {"from": start.date(), "km": compute(pts)}


@router.get("/me/distance/month")
def rider_distance_month(
    rider=Depends(get_current_rider),
    db: Session = Depends(get_db)
):
    start = datetime.utcnow() - timedelta(days=30)
    pts = (
        db.query(GPSLocation)
        .filter(GPSLocation.rider_id == rider.id, GPSLocation.timestamp >= start)
        .order_by(GPSLocation.timestamp)
        .all()
    )
    return {"from": start.date(), "km": compute(pts)}


# ------------------------------------
# Shared distance computation
# ------------------------------------
def compute(points):
    total = 0.0
    for p1, p2 in zip(points, points[1:]):
        total += haversine(
            p1.latitude, p1.longitude,
            p2.latitude, p2.longitude
        )
    return round(total, 3)


# ------------------------------------
# 6. Admin — Leaderboards
# ------------------------------------
@router.get("/admin/distance/day")
def admin_distance_day(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    return report_for(db, start)


@router.get("/admin/distance/week")
def admin_distance_week(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    start = datetime.utcnow() - timedelta(days=7)
    return report_for(db, start)


@router.get("/admin/distance/month")
def admin_distance_month(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    start = datetime.utcnow() - timedelta(days=30)
    return report_for(db, start)


def report_for(db: Session, start):
    riders = db.query(User).filter(User.role == "rider").all()
    board = []

    for r in riders:
        points = (
            db.query(GPSLocation)
            .filter(GPSLocation.rider_id == r.id, GPSLocation.timestamp >= start)
            .order_by(GPSLocation.timestamp)
            .all()
        )
        board.append({
            "login_id": r.login_id,
            "rider_id": r.id,
            "km": compute(points)
        })
    return sorted(board, key=lambda x: x["km"], reverse=True)


# ------------------------------------
# 7. ADMIN — View Rider Route Today
# ------------------------------------
@router.get("/admin/route/{rider_id}")
def admin_route(
    rider_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    pts = (
        db.query(GPSLocation)
        .filter(GPSLocation.rider_id == rider_id, GPSLocation.timestamp >= start)
        .order_by(GPSLocation.timestamp)
        .all()
    )
    return [{
        "lat": p.latitude,
        "lng": p.longitude,
        "time": p.timestamp
    } for p in pts]
