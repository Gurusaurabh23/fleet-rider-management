from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.core.deps import get_current_admin
from app.models.gps import GPSLocation
from app.db.session import SessionLocal
from datetime import datetime

router = APIRouter()

# Store live positions in memory
active_riders = {}  # rider_id -> {"lat": .., "lng": .., "time": ..}


@router.websocket("/ws/location/{rider_id}")
async def rider_location_ws(websocket: WebSocket, rider_id: int):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            lat = data["latitude"]
            lng = data["longitude"]

            # Update in-memory
            active_riders[rider_id] = {
                "latitude": lat,
                "longitude": lng,
                "time": datetime.utcnow()
            }

            # Save to DB
            db = SessionLocal()
            point = GPSLocation(
                rider_id=rider_id,
                latitude=lat,
                longitude=lng,
                timestamp=datetime.utcnow()
            )
            db.add(point)
            db.commit()
            db.close()

    except WebSocketDisconnect:
        active_riders.pop(rider_id, None)


# ✅ C3: Admin fetches all live rider locations
@router.get("/admin/live")
def admin_live_locations(admin=Depends(get_current_admin)):
    return active_riders
