from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import UserCreate, UserRead
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.auth import LoginSchema


router = APIRouter()

@router.post("/login")
def login(credentials: HTTPBasicCredentials = Depends(HTTPBasic()), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.login_id == credentials.username).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    token = create_access_token({"sub": user.login_id, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/register", response_model=UserRead)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    existing = db.query(User).filter(User.login_id == user.login_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Login ID already registered")

    hashed = hash_password(user.password)

    db_user = User(
        login_id=user.login_id,
        email=user.email,
        hashed_password=hashed,
        role="rider",
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


