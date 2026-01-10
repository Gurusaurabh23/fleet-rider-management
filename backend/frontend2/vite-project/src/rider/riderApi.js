let ws = null;
let watchId = null;

// -----------------------------
// 🔔 SHOW BROWSER NOTIFICATION
// -----------------------------
function showNotification(title, message) {
  if (!("Notification" in window)) return;

  if (Notification.permission === "granted") {
    new Notification(title, {
      body: message,
      icon: "/rider-icon.png", // optional
    });
  }
}

// -----------------------------
// ▶ START RIDER SESSION
// -----------------------------
export function startRiderSession(riderId) {
  if (ws) return;

  // ✅ WebSocket connection
  ws = new WebSocket(`ws://127.0.0.1:8000/ws/rider/${riderId}`);

  ws.onopen = () => {
    console.log("🟢 Rider WebSocket connected");
  };

  ws.onclose = () => {
    console.log("🔴 Rider WebSocket disconnected");
    ws = null;
  };

  ws.onerror = (err) => {
    console.error("❌ WebSocket error", err);
  };

  // -----------------------------
  // 🔔 HANDLE BACKEND ALERTS
  // -----------------------------
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log("📩 WS message:", data);

    if (data.type === "STATIONARY_WARNING") {
      showNotification("⏸ Rider Idle", data.message);
    }

    if (data.type === "REDIRECT_TO_ZONE") {
      showNotification(
        "📍 High Demand Area",
        data.message
      );
    }
  };

  // -----------------------------
  // 📡 SEND GPS LOCATION
  // -----------------------------
  watchId = navigator.geolocation.watchPosition(
    (pos) => {
      if (!ws || ws.readyState !== WebSocket.OPEN) return;

      ws.send(
        JSON.stringify({
          lat: pos.coords.latitude,
          lon: pos.coords.longitude,
        })
      );
    },
    (err) => {
      console.error("❌ GPS error:", err);
    },
    {
      enableHighAccuracy: true,
      maximumAge: 5000,
      timeout: 10000,
    }
  );
}

// -----------------------------
// ⏹ STOP RIDER SESSION
// -----------------------------
export function stopRiderSession() {
  if (watchId) {
    navigator.geolocation.clearWatch(watchId);
    watchId = null;
  }

  if (ws) {
    ws.close();
    ws = null;
  }
}
