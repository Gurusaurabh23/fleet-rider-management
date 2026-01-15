from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocketDisconnect
import time

from app.db.session import engine
from app.db.base import Base
from .utils.geo import distance_meters
from .tracking_state import rider_state
from .red_zone_service import (
    get_current_red_zone,
    get_nearest_red_zone,
    get_nearest_under_served_zone
)

from app.routers import (
    auth,
    admin_riders,
    riders_me,
    rider_shifts,
    admin_shifts,
    admin_dashboard,
    tracking,
    dashboard,
    live,
    tracking_admin,
    redzone,
    admin_payroll,
    riders
)
from app.routers import admin_orders

# -------------------------------
# DB Init
# -------------------------------
Base.metadata.create_all(bind=engine)

# -------------------------------
# App
# -------------------------------
app = FastAPI(title="Fleet Backend", version="1.0")

# -------------------------------
# CORS
# -------------------------------
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# Routers 
# -------------------------------
app.include_router(auth.router, prefix="/auth", tags=["Auth"])

# Admin
app.include_router(admin_riders.router, prefix="/admin/riders", tags=["Admin - Riders"])
app.include_router(admin_shifts.router, prefix="/admin/shifts", tags=["Admin - Shifts"])
app.include_router(admin_dashboard.router, prefix="/admin/dashboard", tags=["Admin - Dashboard"])
app.include_router(admin_payroll.router, prefix="/admin/payroll", tags=["Admin - Payroll"])
app.include_router(tracking_admin.router, prefix="/admin/tracking", tags=["Admin - Tracking"])
app.include_router(redzone.router, prefix="/admin/redzones", tags=["Admin - Redzones"])
app.include_router(admin_orders.router)


# Rider 
app.include_router(riders.router, prefix="/riders", tags=["Riders"])        
app.include_router(riders_me.router, prefix="/riders", tags=["Riders"])   
app.include_router(rider_shifts.router, prefix="/riders", tags=["Riders"])  

# Shared
app.include_router(tracking.router, prefix="/tracking", tags=["Tracking"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(live.router, prefix="/live", tags=["Live"])

# -------------------------------
# Tracking Constants
# -------------------------------
RED_ZONE_RADIUS = 500
STATIONARY_LIMIT = 8 * 60

STATIONARY_ALERT_COOLDOWN = 15 * 60
REDIRECT_ALERT_COOLDOWN = 15 * 60

DELIVERY_STOP_TIME = 2 * 60
POST_DELIVERY_COOLDOWN = 20 * 60

# -------------------------------
# Admin WebSocket Store
# -------------------------------
admin_clients = set()

# -------------------------------
# Rider WebSocket
# -------------------------------
@app.websocket("/ws/rider/{rider_id}")
async def rider_tracking(ws: WebSocket, rider_id: str):
    await ws.accept()
    print(f"🚴 Rider connected: {rider_id}")

    try:
        while True:
            data = await ws.receive_json()

            if data.get("type") == "PING":
                continue

            lat = data.get("lat")
            lon = data.get("lon")
            if lat is None or lon is None:
                continue

            now = time.time()

            if rider_id not in rider_state:
                rider_state[rider_id] = {
                    "lat": lat,
                    "lon": lon,
                    "last_move_time": now,
                    "last_update": now,
                    "last_alert": {
                        "STATIONARY": 0,
                        "REDIRECT": 0,
                        "POST_DELIVERY": 0
                    }
                }
            else:
                prev = rider_state[rider_id]
                moved = distance_meters(prev["lat"], prev["lon"], lat, lon)

                if moved > 20:
                    prev["last_move_time"] = now
                    prev["lat"] = lat
                    prev["lon"] = lon

                prev["last_update"] = now

            for admin_ws in list(admin_clients):
                try:
                    await admin_ws.send_json({
                        "rider_id": rider_id,
                        "lat": lat,
                        "lon": lon
                    })
                except:
                    admin_clients.discard(admin_ws)

            last_stationary = rider_state[rider_id]["last_alert"]["STATIONARY"]
            last_redirect = rider_state[rider_id]["last_alert"]["REDIRECT"]
            last_post_delivery = rider_state[rider_id]["last_alert"]["POST_DELIVERY"]

            if now - rider_state[rider_id]["last_move_time"] > STATIONARY_LIMIT:
                if now - last_stationary > STATIONARY_ALERT_COOLDOWN:
                    await ws.send_json({
                        "type": "STATIONARY_WARNING",
                        "message": "You seem idle. Checking nearby high-demand areas."
                    })
                    rider_state[rider_id]["last_alert"]["STATIONARY"] = now

                if now - last_redirect > REDIRECT_ALERT_COOLDOWN:
                    target_zone = get_nearest_under_served_zone(lat, lon, rider_state)
                    if target_zone:
                        await ws.send_json({
                            "type": "REDIRECT_TO_ZONE",
                            "zone_id": target_zone["id"],
                            "lat": target_zone["lat"],
                            "lon": target_zone["lon"],
                            "title": "High demand nearby",
                            "message": (
                                f"{target_zone['id']} has fewer riders. "
                                "Moving there may increase orders."
                            )
                        })
                        rider_state[rider_id]["last_alert"]["REDIRECT"] = now

    except WebSocketDisconnect:
        print(f"⚠️ Rider disconnected: {rider_id}")

# -------------------------------
# Admin WebSocket
# -------------------------------
@app.websocket("/ws/admin")
async def admin_ws(ws: WebSocket):
    await ws.accept()
    admin_clients.add(ws)
    print("🟢 Admin connected. Total:", len(admin_clients))

    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        print("🔴 Admin disconnected")
    finally:
        admin_clients.discard(ws)
