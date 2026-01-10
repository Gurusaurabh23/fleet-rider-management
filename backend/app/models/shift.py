from app.db.base import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime,Float
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base

class ShiftTemplate(Base):
    __tablename__ = "shift_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String)
    start_hour = Column(Integer)
    end_hour = Column(Integer)
    max_capacity = Column(Integer, default=5)


class ShiftBooking(Base):
    __tablename__ = "shift_bookings"

    id = Column(UUID, primary_key=True)
    rider_id = Column(Integer)
    shift_template_id = Column(UUID)
    date = Column(Date)
    status = Column(String)

    # ✅ ADD THESE
    actual_start_time = Column(DateTime, nullable=True)
    actual_end_time = Column(DateTime, nullable=True)
    worked_hours = Column(Float, default=0)
    attendance_status = Column(String)



class Shift(Base):
    __tablename__ = "shifts"

    id = Column(Integer, primary_key=True, index=True)
    rider_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    status = Column(String, default="scheduled")

    hours_worked = Column(Float, nullable=True)
    payout = Column(Float, nullable=True)
    duration_hours = Column(Float, nullable=True)


    rider = relationship("User", back_populates="shifts")
