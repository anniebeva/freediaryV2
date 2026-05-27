from typing import List, Optional
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.models import User
from app.schemas.user import UserCreate


def get_users(db: Session) -> List[User]:
    """Получить всех пользователей"""
    return db.query(User).all()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Получить пользователя по ID"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Получить пользователя по email"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Получить пользователя по username"""
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, user_data: UserCreate) -> User:
    """Создать нового пользователя"""
    raw_password = user_data.password[:72]
    hashed_password = get_password_hash(raw_password)
    
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """Удалить пользователя по ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
    
    db.delete(user)
    db.commit()
    return True
