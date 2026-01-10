from app.db.base import Base
from sqlalchemy import Column, ForeignKey, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from datetime import datetime

class EarningsStatement(Base):
    __tablename__ = "earnings_statements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    rider_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    session_id = Column(UUID(as_uuid=True), ForeignKey("shift_sessions.id"))
    base_salary = Column(Integer)
    delivery_pay = Column(Integer)
    bonus_pay = Column(Integer)
    total_pay = Column(Integer)
    generated_at = Column(DateTime, default=datetime.utcnow)
