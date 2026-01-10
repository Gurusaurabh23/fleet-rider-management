from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, func
from app.db.session import Base

class RedZone(Base):
    __tablename__ = "red_zones"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    radius_meters = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
