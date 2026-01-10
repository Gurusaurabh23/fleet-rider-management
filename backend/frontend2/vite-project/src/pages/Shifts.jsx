import { useEffect, useState } from "react";

export default function Shifts() {
  const [startTime, setStartTime] = useState("");
  const [shifts, setShifts] = useState([]);
  const [riders, setRiders] = useState([]);
  const token = localStorage.getItem("token");

  const loadRiders = async () => {
    const res = await fetch("http://127.0.0.1:8000/admin/riders/", {
      headers: { Authorization: "Bearer " + token },
    });
    if (!res.ok) return alert("Cannot load riders");
    const data = await res.json();
    setRiders(data);
  };

  const loadShifts = async () => {
    const res = await fetch("http://127.0.0.1:8000/admin/shifts/", {
      headers: { Authorization: "Bearer " + token },
    });
    if (!res.ok) return alert("Cannot load shifts");
    const data = await res.json();
    setShifts(data);
  };

  useEffect(() => {
    if (token) {
      loadRiders();
      loadShifts();
    }
  }, []);

  const addShift = async () => {
    if (!token) return alert("No token — login again!");
    if (!startTime) return alert("Pick a date!");

    const iso = new Date(startTime).toISOString();
    const url = `http://127.0.0.1:8000/admin/shifts/?start_time=${encodeURIComponent(
      iso
    )}`;

    const res = await fetch(url, {
      method: "POST",
      headers: { Authorization: "Bearer " + token },
    });

    if (!res.ok) {
      console.log(await res.json());
      return alert("Shift creation failed");
    }

    alert("Shift created!");
    setStartTime("");
    loadShifts();
  };

  const assignRider = async (shiftId, riderId) => {
    if (!riderId) return;
    const res = await fetch(
      `http://127.0.0.1:8000/admin/shifts/${shiftId}/assign/${riderId}`,
      {
        method: "PUT",
        headers: { Authorization: "Bearer " + token },
      }
    );

    if (!res.ok) {
      let msg = "Assign failed";
      try {
        const err = await res.json();
        msg += ": " + (err.detail || JSON.stringify(err));
      } catch {}
      return alert(msg);
    }

    alert("Rider assigned!");
    loadShifts();
  };

  const closeShift = async (shiftId) => {
    const res = await fetch(
      `http://127.0.0.1:8000/admin/shifts/${shiftId}/close`,
      {
        method: "PUT",
        headers: { Authorization: "Bearer " + token },
      }
    );

    if (!res.ok) {
      let msg = "Close failed";
      try {
        const err = await res.json();
        msg += ": " + (err.detail || JSON.stringify(err));
      } catch {}
      return alert(msg);
    }

    alert("Shift closed!");
    loadShifts();
  };

  const deleteShift = async (shiftId) => {
    const res = await fetch(`http://127.0.0.1:8000/admin/shifts/${shiftId}`, {
      method: "DELETE",
      headers: { Authorization: "Bearer " + token },
    });
    if (!res.ok) return alert("Delete failed");
    alert("Shift deleted!");
    loadShifts();
  };

  return (
    <div style={{ padding: "20px" }}>
      <h2>Manage Shifts</h2>

      {/* Create Shift */}
      <div style={{ marginBottom: "20px" }}>
        <input
          type="datetime-local"
          value={startTime}
          onChange={(e) => setStartTime(e.target.value)}
        />
        <button
          onClick={addShift}
          style={{ marginLeft: "10px", padding: "5px 15px" }}
        >
          Add Shift
        </button>
      </div>

      <h3>All Shifts</h3>
      <table border="1" cellPadding="8">
        <thead>
          <tr>
            <th>ID</th>
            <th>Rider Assigned</th>
            <th>Start</th>
            <th>Status</th>
            <th>Attendance</th>
            <th>Worked Hours</th>
            <th>Rate</th>
            <th>Payout</th>
            <th>Assign Rider</th>
            <th>Close</th>
            <th>Delete</th>
          </tr>
        </thead>
        <tbody>
          {shifts.length === 0 && (
            <tr>
              <td colSpan="11">No shifts yet.</td>
            </tr>
          )}

          {shifts.map((s) => (
            <tr key={s.id}>
              <td>{s.id}</td>

              <td>
                {s.rider_id
                  ? riders.find((r) => r.id === s.rider_id)?.login_id
                  : "Unassigned"}
              </td>

              <td>{new Date(s.start_time).toLocaleString()}</td>

              <td>{s.status}</td>

              {/* ✅ NEW: Attendance */}
              <td>
                {s.attendance_status ? s.attendance_status : "-"}
              </td>

              {/* ✅ FIXED: Worked hours */}
              <td>
                {s.worked_hours !== null && s.worked_hours !== undefined
                  ? `${s.worked_hours} hrs`
                  : "-"}
              </td>

              <td>{s.hourly_rate ?? "-"}</td>

              <td>
                {s.payout ? `₹${Number(s.payout).toFixed(2)}` : "-"}
              </td>

              <td>
                {s.status === "completed" ? (
                  "-"
                ) : (
                  <select
                    onChange={(e) => assignRider(s.id, e.target.value)}
                    defaultValue=""
                  >
                    <option value="">Select rider</option>
                    {riders.map((r) => (
                      <option key={r.id} value={r.id}>
                        {r.login_id}
                      </option>
                    ))}
                  </select>
                )}
              </td>

              <td>
                {s.status === "completed" ? (
                  "Done"
                ) : (
                  <button onClick={() => closeShift(s.id)}>Close</button>
                )}
              </td>

              <td>
                <button onClick={() => deleteShift(s.id)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
