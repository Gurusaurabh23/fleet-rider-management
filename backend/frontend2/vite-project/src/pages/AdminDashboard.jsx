import { useEffect, useState } from "react";
import AdminOrdersLeaderboard from "./AdminOrdersLeaderboard";

export default function AdminDashboard() {
  const [file, setFile] = useState(null);
  const [uploadResult, setUploadResult] = useState(null);
  const [error, setError] = useState("");

  // 🆕 LIVE ALERTS STATE
  const [alerts, setAlerts] = useState([]);

  const token = localStorage.getItem("token");

  // -------------------------------
  // 🟢 ADMIN WEBSOCKET (LIVE ALERTS)
  // -------------------------------
  useEffect(() => {
    const ws = new WebSocket("ws://127.0.0.1:8000/ws/admin");

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        // Keep last 20 alerts only
        setAlerts((prev) => [
          {
            time: new Date().toLocaleTimeString(),
            message: `Rider ${data.rider_id} updated location`,
          },
          ...prev.slice(0, 19),
        ]);
      } catch {
        // ignore malformed messages
      }
    };

    ws.onerror = () => {
      console.error("Admin WebSocket error");
    };

    return () => ws.close();
  }, []);

  const uploadCsv = async () => {
    if (!file) {
      alert("Please select a CSV file");
      return;
    }

    if (!token) {
      alert("Admin not authenticated");
      return;
    }

    try {
      setError("");
      setUploadResult(null);

      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch(
        "http://127.0.0.1:8000/admin/dashboard/uber-orders/upload",
        {
          method: "POST",
          headers: {
            Authorization: "Bearer " + token,
          },
          body: formData,
        }
      );

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Upload failed");
      }

      const data = await res.json();
      setUploadResult(data);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div
      style={{
        padding: "32px",
        maxWidth: "1100px",
        margin: "0 auto",
        color: "white",
      }}
    >
      {/* HEADER */}
      <div style={{ marginBottom: "30px" }}>
        <h1 style={{ fontSize: "28px", marginBottom: "6px" }}>
          Admin Dashboard
        </h1>
        <p style={{ color: "#9ca3af" }}>
          Upload weekly Uber Eats data and track rider performance
        </p>
      </div>

      {/* 🆕 LIVE ALERTS PANEL */}
      <div
        style={{
          background: "#020617",
          borderRadius: "14px",
          padding: "20px",
          border: "1px solid #1f2937",
          marginBottom: "40px",
        }}
      >
        <h3 style={{ marginBottom: "12px" }}>🔴 Live Rider Alerts</h3>

        {alerts.length === 0 && (
          <p style={{ color: "#9ca3af" }}>No live activity yet</p>
        )}

        {alerts.map((a, i) => (
          <div
            key={i}
            style={{
              fontSize: "14px",
              padding: "6px 0",
              borderBottom: "1px solid #1f2937",
            }}
          >
            <span style={{ color: "#9ca3af" }}>[{a.time}]</span>{" "}
            <span>{a.message}</span>
          </div>
        ))}
      </div>

      {/* UPLOAD CARD */}
      <div
        style={{
          background: "#111827",
          borderRadius: "14px",
          padding: "24px",
          border: "1px solid #1f2937",
          marginBottom: "40px",
        }}
      >
        <h3 style={{ marginBottom: "16px" }}>
          📤 Upload Uber Eats Weekly Orders
        </h3>

        <div
          style={{
            display: "flex",
            gap: "16px",
            alignItems: "center",
            flexWrap: "wrap",
          }}
        >
          <input
            type="file"
            accept=".csv"
            onChange={(e) => setFile(e.target.files[0])}
            style={{ color: "white" }}
          />

          <button
            onClick={uploadCsv}
            style={{
              padding: "10px 18px",
              borderRadius: "8px",
              border: "none",
              background: "#2563eb",
              color: "white",
              cursor: "pointer",
              fontWeight: "600",
            }}
          >
            Upload CSV
          </button>
        </div>

        {uploadResult && (
          <div
            style={{
              marginTop: "18px",
              background: "#020617",
              padding: "14px",
              borderRadius: "10px",
              border: "1px solid #1f2937",
            }}
          >
            <p>📅 <b>Week start:</b> {uploadResult.week_start}</p>
            <p>✅ <b>Processed:</b> {uploadResult.processed}</p>
            <p>⚠️ <b>Skipped:</b> {uploadResult.skipped}</p>
          </div>
        )}

        {error && (
          <p style={{ marginTop: "10px", color: "#f87171" }}>
            {error}
          </p>
        )}
      </div>

      {/* LEADERBOARD */}
      <div
        style={{
          background: "#111827",
          borderRadius: "14px",
          padding: "24px",
          border: "1px solid #1f2937",
        }}
      >
        <AdminOrdersLeaderboard />
      </div>
    </div>
  );
}
