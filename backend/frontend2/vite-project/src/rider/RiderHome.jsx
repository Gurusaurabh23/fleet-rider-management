import { useState, useRef } from "react";
import { startRiderSession, stopRiderSession } from "./riderApi";

export default function RiderHome() {
  const [riderId, setRiderId] = useState("");
  const [shiftActive, setShiftActive] = useState(false);
  const [status, setStatus] = useState("");

  const [stats, setStats] = useState(null);
  const [statsError, setStatsError] = useState("");

  const wsRef = useRef(null);
  const lastNotificationRef = useRef({});

  // -----------------------
  // LOAD RIDER STATS
  // -----------------------
  const loadStats = async (loginId) => {
    if (!loginId) return;

    try {
      setStatsError("");
      setStats(null);

      const res = await fetch(
        `http://127.0.0.1:8000/riders/stats/${loginId}`
      );
      if (!res.ok) throw new Error("Stats not available");

      const data = await res.json();
      setStats(data);
    } catch {
      setStatsError("Stats not available yet");
    }
  };

  // -----------------------
  // PERMISSIONS
  // -----------------------
  const requestPermissions = async () => {
    try {
      await new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject);
      });

      if ("Notification" in window) {
        const permission = await Notification.requestPermission();
        if (permission !== "granted") {
          alert("Notifications are required.");
        }
      }
      return true;
    } catch {
      alert("Location permission required.");
      return false;
    }
  };

  // -----------------------
  // START SHIFT
  // -----------------------
  const startShift = async () => {
    if (!riderId) {
      alert("Enter Rider ID (e.g. rider1003)");
      return;
    }

    await loadStats(riderId);

    const ok = await requestPermissions();
    if (!ok) return;

    // Start tracking (existing logic)
    startRiderSession(riderId);

    // 🔔 CONNECT WEBSOCKET FOR NOTIFICATIONS
    const ws = new WebSocket(`ws://127.0.0.1:8000/ws/rider/${riderId}`);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      const now = Date.now();

      // cooldown per notification type (15 min)
      const lastTime = lastNotificationRef.current[data.type] || 0;
      if (now - lastTime < 15 * 60 * 1000) return;

      if (data.type === "STATIONARY_WARNING") {
        new Notification("⚠️ Idle Alert", {
          body: data.message,
        });
      }

      if (data.type === "REDIRECT_TO_ZONE") {
        new Notification("📍 High Demand Area", {
          body: data.message,
        });
      }

      lastNotificationRef.current[data.type] = now;
    };

    ws.onerror = () => {
      console.warn("WebSocket error");
    };

    setShiftActive(true);
    setStatus("Shift started. Keep Uber Eats app open.");
  };

  // -----------------------
  // END SHIFT
  // -----------------------
  const endShift = () => {
    stopRiderSession();

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setShiftActive(false);
    setStatus("Shift ended.");
  };

  const tierColor = (tier) => {
    if (tier === "GOLD") return "#facc15";
    if (tier === "SILVER") return "#e5e7eb";
    return "#cd7f32";
  };

  return (
    <div
      style={{
        maxWidth: "420px",
        margin: "40px auto",
        padding: "24px",
        borderRadius: "16px",
        background: "linear-gradient(180deg, #020617, #020617)",
        color: "white",
        boxShadow: "0 25px 50px rgba(0,0,0,0.5)",
      }}
    >
      <h2 style={{ textAlign: "center", marginBottom: "22px" }}>
        🚴 Rider Dashboard
      </h2>

      {stats && (
        <div
          style={{
            background: "#020617",
            border: "1px solid #1e293b",
            padding: "18px",
            borderRadius: "14px",
            marginBottom: "22px",
          }}
        >
          {stats.rank && (
            <p style={{ fontSize: "13px", color: "#94a3b8" }}>
              🏆 Rank <b>#{stats.rank}</b> of {stats.total_riders}
            </p>
          )}

          <h3>📦 {stats.week_orders} orders this week</h3>

          <span
            style={{
              display: "inline-block",
              padding: "6px 14px",
              borderRadius: "999px",
              background: tierColor(stats.tier),
              color: "#020617",
              fontWeight: 800,
              fontSize: "12px",
            }}
          >
            {stats.tier}
          </span>

          {stats.next_tier && (
            <p style={{ marginTop: "12px" }}>
              {stats.orders_to_next_tier} orders to reach{" "}
              <b>{stats.next_tier}</b>
            </p>
          )}

          <div
            style={{
              background: "#1e293b",
              borderRadius: "999px",
              overflow: "hidden",
              height: "10px",
              marginTop: "8px",
            }}
          >
            <div
              style={{
                width: `${stats.progress_percent}%`,
                background: "linear-gradient(90deg, #22c55e, #4ade80)",
                height: "100%",
              }}
            />
          </div>

          <p style={{ marginTop: "14px" }}>
            🎁 Weekly bonus:{" "}
            <b style={{ color: "#facc15" }}>
              {stats.weekly_target_completed
                ? `€${stats.weekly_bonus_amount} unlocked`
                : "Not reached yet"}
            </b>
          </p>
        </div>
      )}

      {!shiftActive && (
        <>
          <input
            type="text"
            placeholder="Enter Rider ID (e.g. rider1003)"
            value={riderId}
            onChange={(e) => setRiderId(e.target.value)}
            style={{
              width: "100%",
              padding: "13px",
              marginBottom: "14px",
              borderRadius: "12px",
              border: "1px solid #1e293b",
              background: "#020617",
              color: "white",
            }}
          />

          <button
            onClick={startShift}
            style={{
              width: "100%",
              padding: "15px",
              borderRadius: "12px",
              background: "linear-gradient(90deg, #22c55e, #4ade80)",
              fontWeight: 800,
              cursor: "pointer",
            }}
          >
            ▶ Start Shift
          </button>
        </>
      )}

      {shiftActive && (
        <button
          onClick={endShift}
          style={{
            width: "100%",
            padding: "15px",
            borderRadius: "12px",
            background: "linear-gradient(90deg, #ef4444, #f87171)",
            color: "white",
            fontWeight: 800,
          }}
        >
          ⏹ End Shift
        </button>
      )}

      {status && (
        <p style={{ marginTop: "18px", textAlign: "center", color: "#94a3b8" }}>
          {status}
        </p>
      )}
    </div>
  );
}
