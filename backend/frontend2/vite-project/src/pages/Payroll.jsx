import { useEffect, useState } from "react";

export default function Payroll() {
  const [year, setYear] = useState(new Date().getFullYear());
  const [month, setMonth] = useState(new Date().getMonth() + 1);
  const [payroll, setPayroll] = useState([]);
  const token = localStorage.getItem("token");

  const loadPayroll = async () => {
    const res = await fetch(
      `http://127.0.0.1:8000/admin/payroll/?year=${year}&month=${month}`,
      {
        headers: {
          Authorization: "Bearer " + token,
        },
      }
    );

    if (!res.ok) {
      alert("Failed to load payroll");
      return;
    }

    const data = await res.json();
    setPayroll(data);
  };

  useEffect(() => {
    loadPayroll();
  }, []);

  return (
    <div style={{ padding: 20 }}>
      <h2>Monthly Payroll</h2>

      {/* Filters */}
      <div style={{ marginBottom: 20 }}>
        <label>Year: </label>
        <input
          type="number"
          value={year}
          onChange={(e) => setYear(e.target.value)}
          style={{ marginRight: 10 }}
        />

        <label>Month: </label>
        <input
          type="number"
          min="1"
          max="12"
          value={month}
          onChange={(e) => setMonth(e.target.value)}
          style={{ marginRight: 10 }}
        />

        <button onClick={loadPayroll}>Load</button>
      </div>

      {/* Table */}
      <table border="1" cellPadding="8">
        <thead>
          <tr>
            <th>Rider</th>
            <th>Total Hours</th>
            <th>Hourly Rate</th>
            <th>Payout</th>
          </tr>
        </thead>
        <tbody>
          {payroll.length === 0 && (
            <tr>
              <td colSpan="4">No data</td>
            </tr>
          )}

          {payroll.map((p, idx) => (
            <tr key={idx}>
              <td>{p.login_id}</td>
              <td>{p.total_hours}</td>
              <td>₹{p.hourly_rate}</td>
              <td>
                <b>₹{Number(p.payout).toFixed(2)}</b>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
