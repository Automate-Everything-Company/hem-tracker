from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session
from ...dependencies import get_db
from ...schemas import UserCreate
from ...crud import get_user_by_username, create_user, is_password_valid

router = APIRouter()


@router.post("/login")
def login(user: UserCreate, db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    db_user = get_user_by_username(db, username=user.username)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if not is_password_valid(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    access_token = authorize.create_access_token(subject=user.username)
    return {"access_token": access_token}


@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = get_user_by_username(db, username=user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    create_user(db, user)
    return {"message": "User created successfully"}
