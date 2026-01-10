from sqlalchemy.orm import Session
from datetime import date
from app.models.gps import GPSLocation
from app.models.daily_distance import DailyDistance
from app.utils import haversine

def compute_daily_distance(db: Session, rider_id: int, day: date):
    points = db.query(GPSLocation).filter(
        GPSLocation.rider_id == rider_id,
        GPSLocation.timestamp >= day,
        GPSLocation.timestamp < day.replace(day=day.day+1)
    ).order_by(GPSLocation.timestamp.asc()).all()

    total = 0
    for p1, p2 in zip(points, points[1:]):
        total += haversine(p1.latitude, p1.longitude, p2.longitude)

    # store or update
    record = db.query(DailyDistance).filter_by(rider_id=rider_id, date=day).first()
    if record:
        record.distance_km = total
    else:
        record = DailyDistance(rider_id=rider_id, date=day, distance_km=total)
        db.add(record)

    db.commit()
    return total
