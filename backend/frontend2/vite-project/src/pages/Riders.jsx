import { useState, useEffect } from "react";

export default function Riders() {
  const [riders, setRiders] = useState([]);
  const [loginId, setLoginId] = useState("");
  const [password, setPassword] = useState("");
  const [jobType, setJobType] = useState("full_time");
  const [hourlyRate, setHourlyRate] = useState("");

  const token = localStorage.getItem("token");

  async function loadRiders() {
    try {
      const res = await fetch("http://127.0.0.1:8000/admin/riders/", {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!res.ok) {
        alert("Error loading riders");
        return;
      }

      const data = await res.json();
      setRiders(data);
    } catch (err) {
      alert("Server error loading riders");
    }
  }

  async function addRider() {
    if (!loginId || !password) {
      alert("Login ID & Password required");
      return;
    }
    if (!hourlyRate) {
      alert("Hourly Rate required");
      return;
    }

    const body = {
      login_id: loginId,
      email: `${loginId}@test.com`,
      password: password,
      role: "rider",
      job_type: jobType,
      hourly_rate: Number(hourlyRate),
    };

    try {
      const res = await fetch("http://127.0.0.1:8000/admin/riders/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(body),
      });

      const data = await res.json();
      console.log(data);

      if (!res.ok) {
        alert("Add rider failed: " + JSON.stringify(data));
        return;
      }

      alert("Rider added!");
      setLoginId("");
      setPassword("");
      setHourlyRate("");
      setJobType("full_time");
      loadRiders();
    } catch (err) {
      alert("Server error");
    }
  }

  useEffect(() => {
    loadRiders();
  }, []);

  return (
    <div style={{ padding: 20 }}>
      <h2>Riders Management</h2>

      <input
        placeholder="login id"
        value={loginId}
        onChange={(e) => setLoginId(e.target.value)}
      />
      <input
        placeholder="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />

      <select value={jobType} onChange={(e) => setJobType(e.target.value)}>
        <option value="full_time">Full Time</option>
        <option value="part_time">Part Time</option>
      </select>

      <input
        placeholder="hourly rate"
        type="number"
        min="1"
        value={hourlyRate}
        onChange={(e) => setHourlyRate(e.target.value)}
      />

      <button onClick={addRider}>Add Rider</button>

      <h3>Existing Riders</h3>
      <ul>
        {riders.map((r) => (
          <li key={r.id}>{r.login_id}</li>
        ))}
      </ul>
    </div>
  );
}
