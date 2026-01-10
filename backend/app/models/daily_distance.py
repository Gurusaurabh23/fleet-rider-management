from sqlalchemy import Column, Integer, Float, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.session import Base

class DailyDistance(Base):
    __tablename__ = "daily_distance"

    id = Column(Integer, primary_key=True, index=True)
    rider_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    distance_km = Column(Float, default=0)

    rider = relationship("User")

    __table_args__ = (UniqueConstraint("rider_id", "date", name="uq_rider_date"), )
