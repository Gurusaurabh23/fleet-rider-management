import asyncio
import websockets
import json
import random

RIDER_ID = "rider_101"
WS_URL = f"ws://127.0.0.1:8000/ws/rider/{RIDER_ID}"

# Starting near red zone
lat = 52.5200
lon = 13.4050


async def simulate_rider():
    async with websockets.connect(WS_URL) as ws:
        print("🚴 Rider connected")

        while True:
            # Simulate small movement
            lat_delta = random.uniform(-0.0003, 0.0003)
            lon_delta = random.uniform(-0.0003, 0.0003)

            data = {
                "lat": lat + lat_delta,
                "lon": lon + lon_delta
            }

            await ws.send(json.dumps(data))
            print("📍 Sent:", data)

            await asyncio.sleep(5)

asyncio.run(simulate_rider())
