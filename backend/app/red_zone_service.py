from math import radians, cos, sin, asin, sqrt

# -------------------------------
# Red Zone Model (In-Memory)
# -------------------------------
RED_ZONES = [
    {
        "id": "zone_1",
        "lat": 52.5200,   # Berlin Center
        "lon": 13.4050,
        "radius": 500,
        "weight": 3,
    },
    {
        "id": "zone_2",
        "lat": 52.4909,   # Kreuzberg
        "lon": 13.3929,
        "radius": 500,
        "weight": 2,
    },
    {
        "id": "zone_3",
        "lat": 52.5076,   # Mitte
        "lon": 13.3904,
        "radius": 500,
        "weight": 1,
    },
]

# -------------------------------
# Utils
# -------------------------------
def distance_meters(lat1, lon1, lat2, lon2):
    R = 6371000
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * R * asin(sqrt(a))

# -------------------------------
# Public API (Backward Compatible)
# -------------------------------
def get_all_red_zones():
    return RED_ZONES


def get_current_red_zone(lat=None, lon=None):
    """
    BACKWARD COMPATIBILITY METHOD

    If lat/lon provided → return zone rider is in
    Else → return highest-weight zone (default behavior)
    """
    if lat is not None and lon is not None:
        for zone in RED_ZONES:
            if distance_meters(lat, lon, zone["lat"], zone["lon"]) <= zone["radius"]:
                return zone
        return None

    # Default: highest priority zone
    return max(RED_ZONES, key=lambda z: z["weight"])


def get_nearest_red_zone(lat, lon):
    nearest = None
    min_dist = float("inf")

    for zone in RED_ZONES:
        dist = distance_meters(lat, lon, zone["lat"], zone["lon"])
        if dist < min_dist:
            min_dist = dist
            nearest = zone

    return nearest


def get_zone_for_rider(lat, lon):
    for zone in RED_ZONES:
        if distance_meters(lat, lon, zone["lat"], zone["lon"]) <= zone["radius"]:
            return zone
    return None


def compute_zone_loads(rider_state):
    zones = get_all_red_zones()
    total_riders = len(rider_state)

    if total_riders == 0:
        return {}

    total_weight = sum(z["weight"] for z in zones)
    zone_counts = {z["id"]: 0 for z in zones}

    for rider in rider_state.values():
        zone = get_zone_for_rider(rider["lat"], rider["lon"])
        if zone:
            zone_counts[zone["id"]] += 1

    result = {}
    for z in zones:
        target = (z["weight"] / total_weight) * total_riders
        current = zone_counts[z["id"]]

        result[z["id"]] = {
            "current": current,
            "target": round(target, 1),
            "pressure": round(current / target, 2) if target > 0 else 0
        }

    return result

def get_nearest_under_served_zone(lat, lon, rider_state):
    """
    Returns nearest red zone where pressure < 1.0
    """
    zone_loads = compute_zone_loads(rider_state)

    candidates = []
    for zone in RED_ZONES:
        load = zone_loads.get(zone["id"])
        if not load:
            continue

        # Under-served zone
        if load["pressure"] < 1.0:
            dist = distance_meters(lat, lon, zone["lat"], zone["lon"])
            candidates.append((dist, zone))

    if not candidates:
        return None

    # Return nearest under-served zone
    candidates.sort(key=lambda x: x[0])
    return candidates[0][1]


def update_zone_weight(zone_id: str, weight: int):
    for zone in RED_ZONES:
        if zone["id"] == zone_id:
            zone["weight"] = max(1, min(weight, 5))  # clamp 1–5
            return zone
    return None

