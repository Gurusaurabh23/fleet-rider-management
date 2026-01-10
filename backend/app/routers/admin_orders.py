from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta

from app.db.session import get_db
from app.core.deps import get_current_admin
from app.models.user import User
from app.models.rider_weekly_orders import RiderWeeklyOrders

router = APIRouter(prefix="/admin/orders", tags=["Admin - Orders"])


@router.get("/leaderboard")
def weekly_orders_leaderboard(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    week_start = date.today() - timedelta(days=7)

    results = (
        db.query(
            User.id.label("rider_id"),
            User.login_id,
            func.sum(RiderWeeklyOrders.completed_orders).label("orders")
        )
        .join(RiderWeeklyOrders, RiderWeeklyOrders.rider_id == User.id)
        .filter(RiderWeeklyOrders.week_start >= week_start)
        .group_by(User.id)
        .order_by(func.sum(RiderWeeklyOrders.completed_orders).desc())
        .all()
    )

    return [
        {
            "rider_id": r.rider_id,
            "login_id": r.login_id,
            "orders": int(r.orders or 0)
        }
        for r in results
    ]
