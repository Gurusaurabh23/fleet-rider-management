import { useEffect, useState } from "react";

export default function AdminOrdersLeaderboard() {
  const [rows, setRows] = useState([]);
  const [error, setError] = useState("");
  const token = localStorage.getItem("token");

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setError("");

      const res = await fetch(
        "http://127.0.0.1:8000/riders/leaderboard",
        {
          headers: {
            Authorization: "Bearer " + token,
          },
        }
      );

      if (!res.ok) {
        throw new Error("Failed to load leaderboard");
      }

      const json = await res.json();
      setRows(json.leaderboard || []);
    } catch (err) {
      console.error(err);
      setError("Could not load performance data");
    }
  };

  const getTierMeta = (orders) => {
    if (orders >= 80) return { tier: "GOLD", bonus: 50, color: "#facc15" };
    if (orders >= 40) return { tier: "SILVER", bonus: 20, color: "#e5e7eb" };
    return { tier: "BRONZE", bonus: 0, color: "#d97706" };
  };

  const rankIcon = (rank) => {
    if (rank === 1) return "🥇";
    if (rank === 2) return "🥈";
    if (rank === 3) return "🥉";
    return rank;
  };

  // ---------------------------
  // 📤 CSV EXPORT
  // ---------------------------
  const exportCsv = () => {
    if (rows.length === 0) {
      alert("No data to export");
      return;
    }

    const header = [
      "rank",
      "login_id",
      "completed_orders",
      "tier",
      "weekly_bonus",
    ];

    const csvRows = rows.map((r, index) => {
      const meta = getTierMeta(r.completed_orders);
      return [
        index + 1,
        r.login_id,
        r.completed_orders,
        meta.tier,
        meta.bonus,
      ].join(",");
    });

    const csvContent =
      header.join(",") + "\n" + csvRows.join("\n");

    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = `weekly_rider_performance_${new Date()
      .toISOString()
      .slice(0, 10)}.csv`;
    a.click();

    window.URL.revokeObjectURL(url);
  };

  return (
    <div
      style={{
        marginTop: "40px",
        background: "white",
        padding: "24px",
        borderRadius: "12px",
        boxShadow: "0 10px 20px rgba(0,0,0,0.08)",
      }}
    >
      {/* Header */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "20px",
        }}
      >
        <h2 style={{ margin: 0 }}>🏆 Weekly Orders Leaderboard</h2>

        <button
          onClick={exportCsv}
          style={{
            padding: "8px 14px",
            borderRadius: "8px",
            border: "none",
            background: "#16a34a",
            color: "white",
            cursor: "pointer",
            fontWeight: 600,
          }}
        >
          ⬇ Export CSV
        </button>
      </div>

      {error && <p style={{ color: "#dc2626" }}>{error}</p>}

      {/* Table */}
      <div style={{ overflowX: "auto" }}>
        <table
          style={{
            width: "100%",
            borderCollapse: "collapse",
            fontSize: "14px",
          }}
        >
          <thead>
            <tr style={{ background: "#f9fafb" }}>
              <th style={th}>Rank</th>
              <th style={th}>Rider</th>
              <th style={th}>Orders</th>
              <th style={th}>Tier</th>
              <th style={th}>Weekly Bonus</th>
            </tr>
          </thead>

          <tbody>
            {rows.length === 0 && (
              <tr>
                <td colSpan="5" style={{ textAlign: "center", padding: "20px" }}>
                  No data yet
                </td>
              </tr>
            )}

            {rows.map((r, index) => {
              const meta = getTierMeta(r.completed_orders);

              return (
                <tr
                  key={r.rider_id}
                  style={{
                    background:
                      index < 3 ? "#fefce8" : "transparent",
                  }}
                >
                  <td style={td}>{rankIcon(index + 1)}</td>
                  <td style={td}>{r.login_id}</td>
                  <td style={td}>
                    <b>{r.completed_orders}</b>
                  </td>
                  <td style={td}>
                    <span
                      style={{
                        padding: "4px 10px",
                        borderRadius: "999px",
                        fontWeight: 600,
                        background: meta.color,
                        color:
                          meta.tier === "GOLD"
                            ? "#92400e"
                            : "#111827",
                      }}
                    >
                      {meta.tier}
                    </span>
                  </td>
                  <td style={td}>
                    {meta.bonus > 0 ? (
                      <span
                        style={{
                          color: "#16a34a",
                          fontWeight: 600,
                        }}
                      >
                        €{meta.bonus}
                      </span>
                    ) : (
                      "—"
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

const th = {
  padding: "12px",
  borderBottom: "1px solid #e5e7eb",
  textAlign: "left",
  fontWeight: 600,
  color: "#374151",
};

const td = {
  padding: "12px",
  borderBottom: "1px solid #f1f5f9",
};
