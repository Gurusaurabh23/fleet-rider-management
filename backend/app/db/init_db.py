from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.user import User
from app.models.user import User
from app.models.shift import Shift


db = SessionLocal()

admin = User(
    email="admin@fleet.com",
    hashed_password=hash_password("Admin@123"),
    is_admin=True
)
db.add(admin)
db.commit()
db.close()
print("Admin created!")
