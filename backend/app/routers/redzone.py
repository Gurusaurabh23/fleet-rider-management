from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.core.deps import get_current_admin
from app.models.redzone import RedZone
from app.schemas.redzone import RedZoneCreate, RedZoneRead

from app.tracking_state import rider_state
from app.red_zone_service import (
    compute_zone_loads,
    get_all_red_zones,
    update_zone_weight
)

router = APIRouter()

# -------------------------------
# DB RED ZONE CRUD (UNCHANGED)
# -------------------------------
@router.post("/", response_model=RedZoneRead, status_code=201)
def create_red_zone(
    data: RedZoneCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    zone = RedZone(**data.model_dump())
    db.add(zone)
    db.commit()
    db.refresh(zone)
    return zone


@router.get("/", response_model=List[RedZoneRead])
def list_red_zones(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    return db.query(RedZone).all()


@router.put("/{zone_id}", response_model=RedZoneRead)
def update_red_zone(
    zone_id: int,
    data: RedZoneCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    zone = db.query(RedZone).filter(RedZone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    for key, value in data.model_dump().items():
        setattr(zone, key, value)

    db.commit()
    db.refresh(zone)
    return zone


@router.delete("/{zone_id}")
def delete_red_zone(
    zone_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    zone = db.query(RedZone).filter(RedZone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    db.delete(zone)
    db.commit()
    return {"message": "Zone deleted"}

# -------------------------------
# 🔥 LIVE ZONE STATUS (STEP C4)
# -------------------------------
@router.get("/status")
def red_zone_status():
    loads = compute_zone_loads(rider_state)
    zones = get_all_red_zones()

    result = []
    for zone in zones:
        load = loads.get(zone["id"], {})
        pressure = load.get("pressure", 0)

        if pressure < 0.8:
            color = "green"
        elif pressure <= 1.2:
            color = "yellow"
        else:
            color = "red"

        result.append({
            "id": zone["id"],
            "lat": zone["lat"],
            "lon": zone["lon"],
            "radius": zone["radius"],
            "weight": zone["weight"],
            "pressure": pressure,
            "color": color,
        })

    return result

# -------------------------------
# 🧠 STEP C7 — UPDATE ZONE WEIGHT (LIVE)
# -------------------------------
@router.put("/weight/{zone_id}")
def update_zone_weight_api(
    zone_id: str,
    weight: int,
    admin=Depends(get_current_admin)
):
    zone = update_zone_weight(zone_id, weight)
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    return {
        "message": "Zone weight updated",
        "zone": zone
    }
