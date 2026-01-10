from pydantic import BaseModel


class MonthlyPayroll(BaseModel):
    rider_id: int
    login_id: str
    year: int
    month: int
    total_hours: float
    hourly_rate: float
    payout: float

    class Config:
        from_attributes = True
