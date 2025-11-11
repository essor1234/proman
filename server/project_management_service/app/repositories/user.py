# project_service/app/repositories/user.py
"""
Repository layer for User CRUD operations.
- Isolates SQLAlchemy queries from FastAPI routes.
- Makes testing easier (mock repository).
- Follows separation of concerns.
"""

from sqlalchemy.orm import Session
from models.user import User as UserModel
from schemas.user import UserCreate, UserUpdate

# CREATE
def create_user(db: Session, user: UserCreate):
    db_user = UserModel(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# READ ALL
def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(UserModel).offset(skip).limit(limit).all()

# READ ONE
def get_user(db: Session, user_id: int):
    return db.query(UserModel).filter(UserModel.id == user_id).first()

# UPDATE
def update_user(db: Session, user_id: int, user_update: UserUpdate):
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    if user_update.name is not None:
        db_user.name = user_update.name
    if user_update.email is not None:
        db_user.email = user_update.email
    db.commit()
    db.refresh(db_user)
    return db_user

# DELETE
def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user