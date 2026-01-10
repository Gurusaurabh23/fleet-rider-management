from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict
from app.core.deps import get_current_rider

router = APIRouter()

active_connections: Dict[int, WebSocket] = {}

@router.websocket("/ws/gps")
async def gps_websocket(
    websocket: WebSocket,
):
    # accept rider socket
    await websocket.accept()

    # first message must contain rider_id
    data = await websocket.receive_json()
    rider_id = data.get("rider_id")

    if not rider_id:
        await websocket.close()
        return

    active_connections[rider_id] = websocket

    try:
        while True:
            message = await websocket.receive_json()
            # Expect { "lat": ..., "lng": ... }
            print(f"Rider {rider_id}: {message}")
            # Echo for testing
            await websocket.send_json({"status": "received", "data": message})

    except WebSocketDisconnect:
        active_connections.pop(rider_id, None)
        print(f"Rider {rider_id} disconnected")
