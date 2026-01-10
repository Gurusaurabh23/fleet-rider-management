from app.db.base import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4

class ShiftSession(Base):
    __tablename__ = "shift_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    rider_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    booking_id = Column(UUID(as_uuid=True), ForeignKey("shift_bookings.id"))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    total_minutes = Column(Integer)
