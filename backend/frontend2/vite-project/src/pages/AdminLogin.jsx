import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function AdminLogin() {
  const [loginId, setLoginId] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();

    const res = await fetch("http://127.0.0.1:8000/auth/login", {
      method: "POST",
      headers: {
        Authorization: "Basic " + btoa(`${loginId}:${password}`),
      },
    });

    if (res.ok) {
      const data = await res.json();
      localStorage.setItem("token", data.access_token);
      navigate("/admin");
    } else {
      alert("Invalid credentials");
    }
  };

  return (
    <div>
      <h2>Admin Login</h2>
      <form onSubmit={handleLogin}>
        <input
          value={loginId}
          onChange={(e) => setLoginId(e.target.value)}
          placeholder="Login ID"
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
        />
        <button type="submit">Login</button>
      </form>
    </div>
  );
}
