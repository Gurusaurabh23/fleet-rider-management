from sqlalchemy import Column, Integer, Float, Date, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.db.session import Base


class Bonus(Base):
    __tablename__ = "bonus"

    id = Column(Integer, primary_key=True, index=True)
    rider_id = Column(Integer, ForeignKey("users.id"))
    week_start = Column(Date, nullable=False)
    amount = Column(Float, default=0)
    created_at = Column(DateTime, server_default=func.now())

    rider = relationship("User")

    # -------------------------------
    # BONUS CALCULATION LOGIC
    # -------------------------------
    @staticmethod
    def calculate_weekly_bonus(total_hours):
        """
        Weekly performance bonus based on worked hours
        """

        if total_hours >= 50:
            return 40
        elif total_hours >= 40:
            return 25
        return 0

    @staticmethod
    def calculate_weekly_tier(total_hours, no_show_count):
        """
        Returns rider performance tier for the week
        """

        if total_hours >= 50 and no_show_count == 0:
            return "GOLD"
        elif total_hours >= 35:
            return "SILVER"
        return "BRONZE"

