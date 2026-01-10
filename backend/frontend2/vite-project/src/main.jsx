import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import "mapbox-gl/dist/mapbox-gl.css"; // ✅ REQUIRED for Mapbox markers
import App from "./App.jsx";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <App />
  </StrictMode>
);
