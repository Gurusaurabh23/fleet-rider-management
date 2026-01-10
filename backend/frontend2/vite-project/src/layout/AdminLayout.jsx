import { Outlet, useNavigate } from "react-router-dom";
import { removeToken } from "../auth";
import { useEffect } from "react";

export default function AdminLayout() {
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");

    // ❗ ONLY protect admin routes
    if (!token) {
      navigate("/", { replace: true });
    }
  }, [navigate]);

  const logout = () => {
    removeToken();
    navigate("/", { replace: true });
  };

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      {/* Sidebar */}
      <div
        style={{
          width: "220px",
          background: "#222",
          color: "white",
          padding: "20px",
        }}
      >
        <h2 style={{ color: "#61dafb" }}>Admin</h2>

        <div style={{ marginTop: "30px" }}>
          <div style={{ margin: "15px 0", cursor: "pointer" }} onClick={() => navigate("/admin")}>
            Dashboard
          </div>
          <div style={{ margin: "15px 0", cursor: "pointer" }} onClick={() => navigate("/admin/riders")}>
            Riders
          </div>
          <div style={{ margin: "15px 0", cursor: "pointer" }} onClick={() => navigate("/admin/shifts")}>
            Shifts
          </div>
          <div style={{ margin: "15px 0", cursor: "pointer" }} onClick={() => navigate("/admin/tracking")}>
            Tracking
          </div>
          <div style={{ margin: "15px 0", cursor: "pointer" }} onClick={() => navigate("/admin/payroll")}>
            Payroll
          </div>
        </div>

        <div
          style={{ marginTop: "50px", color: "yellow", cursor: "pointer" }}
          onClick={logout}
        >
          Logout
        </div>
      </div>

      {/* Content */}
      <div style={{ flex: 1, padding: "25px" }}>
        <Outlet />
      </div>
    </div>
  );
}
