import { useEffect, useState } from "react";

export default function AdminWeeklyImpact() {
  const [stats, setStats] = useState(null);
  const token = localStorage.getItem("token");

  useEffect(() => {
    loadImpact();
  }, []);

  const loadImpact = async () => {
    try {
      const res = await fetch(
        "http://127.0.0.1:8000/riders/leaderboard",
        {
          headers: {
            Authorization: "Bearer " + token,
          },
        }
      );

      if (!res.ok) return;

      const data = await res.json();

      // Simple derived insights
      const totalOrders = data.leaderboard.reduce(
        (sum, r) => sum + r.completed_orders,
        0
      );

      const goldRiders = data.leaderboard.filter(
        (r) => r.completed_orders >= 80
      ).length;

      const silverRiders = data.leaderboard.filter(
        (r) => r.completed_orders >= 40 && r.completed_orders < 80
      ).length;

      setStats({
        totalOrders,
        goldRiders,
        silverRiders,
        totalRiders: data.leaderboard.length,
      });
    } catch (err) {
      console.error(err);
    }
  };

  if (!stats) return null;

  return (
    <div
      style={{
        background: "#020617",
        borderRadius: "14px",
        padding: "24px",
        border: "1px solid #1f2937",
        marginBottom: "40px",
      }}
    >
      <h3 style={{ marginBottom: "16px" }}>
        📈 Weekly Fleet Impact
      </h3>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
          gap: "20px",
        }}
      >
        <StatCard label="Total Orders" value={stats.totalOrders} />
        <StatCard label="Gold Riders" value={stats.goldRiders} />
        <StatCard label="Silver Riders" value={stats.silverRiders} />
        <StatCard label="Active Riders" value={stats.totalRiders} />
      </div>
    </div>
  );
}

function StatCard({ label, value }) {
  return (
    <div
      style={{
        background: "#111827",
        padding: "18px",
        borderRadius: "12px",
        border: "1px solid #1f2937",
      }}
    >
      <p style={{ fontSize: "14px", color: "#9ca3af" }}>
        {label}
      </p>
      <p
        style={{
          fontSize: "26px",
          fontWeight: "bold",
          marginTop: "6px",
        }}
      >
        {value}
      </p>
    </div>
  );
}
