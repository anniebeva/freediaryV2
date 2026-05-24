from sqlalchemy.orm import Session
from datetime import datetime as dt, timedelta, date, timezone
from typing import Optional

from app.models.models import SessionTracking


def cleanup_expired_sessions(db: Session, max_age_hours: int = 24) -> int:
    """
    Очистить просроченные сессии
    
    Args:
        db: Сессия базы данных
        max_age_hours: Максимальный возраст сессии в часах (по умолчанию 24)
    
    Returns:
        Количество удаленных сессий
    """
    cutoff_time = dt.now(timezone.utc) - timedelta(hours=max_age_hours)
    
    # Находим все сессии, которые истекли
    expired_sessions = db.query(SessionTracking).filter(
        SessionTracking.expires_at < dt.now(timezone.utc)
    ).all()
    
    deleted_count = 0
    for session in expired_sessions:
        db.delete(session)
        deleted_count += 1
    
    if deleted_count > 0:
        db.commit()
    
    return deleted_count


def refresh_session_access(db: Session, session_id: str) -> Optional[SessionTracking]:
    """
    Обновить время последнего доступа к сессии
    """
    db.query(SessionTracking).filter(
        SessionTracking.session_id == session_id
    ).update({'last_accessed': dt.now(timezone.utc)})
    db.commit()
    
    return db.query(SessionTracking).filter(
        SessionTracking.session_id == session_id
    ).first()


def create_or_get_session(db: Session, session_id: str) -> SessionTracking:
    """
    Создать новую сессию или получить существующую
    
    Args:
        db: Сессия базы данных
        session_id: Идентификатор сессии
    
    Returns:
        Сессия (новая или существующая)
    """
    session = db.query(SessionTracking).filter(
        SessionTracking.session_id == session_id
    ).first()
    
    if not session:
        # Создаем новую сессию с истечением через 24 часа
        expires_at = dt.now(timezone.utc) + timedelta(hours=24)
        session = SessionTracking(
            session_id=session_id,
            expires_at=expires_at
        )
        db.add(session)
        db.commit()
        db.refresh(session)
    else:
        # Обновляем время последнего доступа
        session = refresh_session_access(db, session_id)
    
    return session


def get_session_info(db: Session, session_id: str) -> Optional[dict]:
    """
    Получить информацию о сессии
    
    Args:
        db: Сессия базы данных
        session_id: Идентификатор сессии
    
    Returns:
        Словарь с информацией о сессии или None
    """
    session = db.query(SessionTracking).filter(
        SessionTracking.session_id == session_id
    ).first()
    
    if not session:
        return None
    
    return {
        "session_id": session.session_id,
        "created_at": session.created_at,
        "expires_at": session.expires_at,
        "last_accessed": session.last_accessed,
        "is_expired": session.expires_at < dt.now(timezone.utc)
    }