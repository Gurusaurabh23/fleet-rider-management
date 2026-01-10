import { useEffect, useRef } from "react";
import mapboxgl from "mapbox-gl";

mapboxgl.accessToken =
  "pk.eyJ1IjoiZ3VydTIzIiwiYSI6ImNtamltc2I2djF1b2UzZ3NoMWpyMWtzY2QifQ.9uc3J3OuEUGV__J76lbwEw";

export default function Tracking() {
  const mapContainerRef = useRef(null);
  const mapRef = useRef(null);
  const markersRef = useRef({});
  const wsRef = useRef(null);
  const zoneIntervalRef = useRef(null);

  // 🔁 Draw / Update Zones
  const drawZones = async () => {
    if (!mapRef.current) return;

    const res = await fetch("http://127.0.0.1:8000/admin/redzones/status");
    const zones = await res.json();

    zones.forEach((zone) => {
      const sourceId = `zone-source-${zone.id}`;
      const layerId = `zone-layer-${zone.id}`;

      const geojson = {
        type: "Feature",
        geometry: {
          type: "Point",
          coordinates: [zone.lon, zone.lat],
        },
      };

      // ✅ Update existing source
      if (mapRef.current.getSource(sourceId)) {
        mapRef.current.getSource(sourceId).setData(geojson);
      } else {
        // ✅ Create source
        mapRef.current.addSource(sourceId, {
          type: "geojson",
          data: geojson,
        });

        // ✅ Create layer
        mapRef.current.addLayer({
          id: layerId,
          type: "circle",
          source: sourceId,
          paint: {
            "circle-radius": zone.radius / 8, // BIGGER & clearer
            "circle-color":
              zone.color === "green"
                ? "#22c55e"
                : zone.color === "yellow"
                ? "#eab308"
                : "#ef4444",
            "circle-opacity": 0.35,
          },
        });
      }
    });
  };

  useEffect(() => {
    // 🗺️ Init map
    mapRef.current = new mapboxgl.Map({
      container: mapContainerRef.current,
      style: "mapbox://styles/mapbox/dark-v11",
      center: [13.3929, 52.491], // Berlin
      zoom: 12,
    });

    mapRef.current.on("load", async () => {
      console.log("🗺️ Map loaded");

      // Initial zone draw
      await drawZones();

      // Refresh zones every 5s
      zoneIntervalRef.current = setInterval(drawZones, 5000);

      // 🔌 Admin WebSocket
      wsRef.current = new WebSocket("ws://127.0.0.1:8000/ws/admin");

      wsRef.current.onmessage = (event) => {
        const { rider_id, lat, lon } = JSON.parse(event.data);
        if (!rider_id || lat == null || lon == null) return;

        if (!markersRef.current[rider_id]) {
          const el = document.createElement("div");
          el.style.width = "18px";
          el.style.height = "18px";
          el.style.borderRadius = "50%";
          el.style.background = "#22d3ee";
          el.style.boxShadow = "0 0 15px #22d3ee";

          markersRef.current[rider_id] = new mapboxgl.Marker(el)
            .setLngLat([lon, lat])
            .addTo(mapRef.current);
        } else {
          markersRef.current[rider_id].setLngLat([lon, lat]);
        }
      };
    });

    return () => {
      if (wsRef.current) wsRef.current.close();
      if (zoneIntervalRef.current)
        clearInterval(zoneIntervalRef.current);
      if (mapRef.current) mapRef.current.remove();
    };
  }, []);

  return (
    <div>
      <h2>Live Rider Tracking</h2>
      <div
        ref={mapContainerRef}
        style={{
          height: "80vh",
          borderRadius: "12px",
          overflow: "hidden",
        }}
      />
    </div>
  );
}
