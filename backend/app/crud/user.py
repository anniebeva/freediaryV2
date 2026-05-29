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


def get_user_by_telegram_id(db: Session, telegram_id: str) -> Optional[User]:
    """Получить пользователя по telegram_id"""
    return db.query(User).filter(User.telegram_id == telegram_id).first()


def update_user_telegram_id(db: Session, user_id: int, telegram_id: str) -> Optional[User]:
    """Обновить telegram_id пользователя"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    
    user.telegram_id = telegram_id  # type: ignore
    db.commit()
    db.refresh(user)
    return user


def unlink_user_telegram(db: Session, user_id: int) -> Optional[User]:
    """Отвязать Telegram от пользователя"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    
    user.telegram_id = None  # type: ignore
    user.telegram_notifications_enabled = False  # type: ignore
    db.commit()
    db.refresh(user)
    return user


def update_telegram_notifications(db: Session, user_id: int, enabled: bool) -> Optional[User]:
    """Обновить настройки Telegram уведомлений"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    
    user.telegram_notifications_enabled = enabled  # type: ignore
    db.commit()
    db.refresh(user)
    return user
