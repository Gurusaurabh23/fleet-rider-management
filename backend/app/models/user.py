from sqlalchemy import Column, Integer, String, Boolean, DateTime, func,Float
from sqlalchemy.orm import relationship
from app.db.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    login_id = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    role = Column(String, nullable=False, server_default="admin")   # admin or rider
    job_type = Column(String, nullable=False, server_default="fulltime")  # NEW fulltime / parttime
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    hourly_rate = Column(Float, nullable=True)

    shifts = relationship("Shift", back_populates="rider")
    gps_locations = relationship("GPSLocation", back_populates="rider")

