from sqlalchemy.orm import Session

from backend.src.common.security import pwd_context
from backend.src.database import models
from backend.src.users import schemas


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        password=hashed_password,
        email=user.email,
        peak_level=user.peak_level,
        weekly_infusions=user.weekly_infusions
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
