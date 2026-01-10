import { BrowserRouter, Routes, Route } from "react-router-dom";
import AdminLogin from "./pages/AdminLogin";
import AdminLayout from "./layout/AdminLayout";
import AdminDashboard from "./pages/AdminDashboard";
import Riders from "./pages/Riders";
import Shifts from "./pages/Shifts";
import Tracking from "./pages/Tracking";
import Payroll from "./pages/Payroll";

// ✅ Rider App
import RiderHome from "./rider/RiderHome";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Admin Login */}
        <Route path="/" element={<AdminLogin />} />

        {/* Rider Web App (PUBLIC) */}
        <Route path="/rider" element={<RiderHome />} />

        {/* Admin Protected Routes */}
        <Route path="/admin" element={<AdminLayout />}>
          <Route index element={<AdminDashboard />} />
          <Route path="riders" element={<Riders />} />
          <Route path="shifts" element={<Shifts />} />
          <Route path="tracking" element={<Tracking />} />
          <Route path="payroll" element={<Payroll />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
