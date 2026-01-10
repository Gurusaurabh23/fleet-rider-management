from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class RiderWeeklyOrders(Base):
    __tablename__ = "rider_weekly_orders"

    id = Column(Integer, primary_key=True, index=True)

    rider_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    week_start = Column(Date, nullable=False)
    completed_orders = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # optional relationship (safe to keep)
    rider = relationship("User")
