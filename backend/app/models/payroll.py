from sqlalchemy import Column, Integer, Date, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.db.session import Base

# business constants (can be moved later if needed)
MIN_DAILY_HOURS_FOR_BONUS = 6
DAILY_BONUS_AMOUNT = 5


class Payroll(Base):
    __tablename__ = "payroll"

    id = Column(Integer, primary_key=True, index=True)
    rider_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date, nullable=False)

    total_hours = Column(Float, default=0)
    amount = Column(Float, default=0)

    created_at = Column(DateTime, server_default=func.now())

    rider = relationship("User")

    # -------------------------------
    # PAYROLL CALCULATION LOGIC
    # -------------------------------
    @staticmethod
    def calculate_for_shift(shift_booking):
        """
        Creates a Payroll record from a ShiftBooking.
        Assumes:
        - shift_booking.worked_hours exists
        - shift_booking.attendance_status exists
        - rider has hourly_rate
        """

        # NO SHOW → no pay
        if shift_booking.attendance_status == "NO_SHOW":
            total_hours = 0
            amount = 0
            return total_hours, amount

        total_hours = shift_booking.worked_hours or 0

        hourly_rate = shift_booking.rider.hourly_rate
        amount = total_hours * hourly_rate

        # Daily incentive (simple & safe)
        if (
            shift_booking.attendance_status == "PRESENT"
            and total_hours >= MIN_DAILY_HOURS_FOR_BONUS
        ):
            amount += DAILY_BONUS_AMOUNT

        return round(total_hours, 2), round(amount, 2)
