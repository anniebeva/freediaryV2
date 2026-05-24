from typing import List, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.models import Exercise, SessionExercise, Training, SessionTraining
from app.schemas.exercise import ExerciseCreate, ExerciseUpdate


def get_exercises_by_training_id(db: Session, training_id: int, user_id: int, session_id: Optional[str] = None) -> List[Union[Exercise, SessionExercise]]:
    """Получить упражнения для тренировки в зависимости от типа пользователя"""
    if user_id > 0:
        # Зарегистрированный пользователь - получаем упражнения из обычной тренировки
        return db.query(Exercise).filter(Exercise.training_id == training_id).all()
    elif user_id == 0 and session_id:
        # Гостевой пользователь - получаем упражнения из сессионной тренировки
        return db.query(SessionExercise).filter(
            SessionExercise.training_id == training_id,
            SessionExercise.session_id == session_id
        ).all()
    else:
        return []


def get_exercise_by_id(db: Session, exercise_id: int, user_id: int, session_id: Optional[str] = None) -> Optional[Union[Exercise, SessionExercise]]:
    """Получить упражнение по ID в зависимости от типа пользователя"""
    if user_id > 0:
        # Зарегистрированный пользователь - ищем в обычных упражнениях
        return db.query(Exercise).filter(Exercise.id == exercise_id).first()
    elif user_id == 0 and session_id:
        # Гостевой пользователь - ищем в сессионных упражнениях
        return db.query(SessionExercise).filter(
            SessionExercise.id == exercise_id,
            SessionExercise.session_id == session_id
        ).first()
    return None


def create_exercise(db: Session, exercise_data: ExerciseCreate, user_id: int, session_id: Optional[str] = None) -> Optional[Union[Exercise, SessionExercise]]:
    """Создать новое упражнение"""
    # Проверяем существование тренировки
    if user_id > 0:
        # Для зарегистрированного пользователя ищем обычную тренировку
        training = db.query(Training).filter(
            Training.id == exercise_data.training_id,
            Training.user_id == user_id
        ).first()
    elif user_id == 0 and session_id:
        # Для гостевого пользователя ищем сессионную тренировку
        training = db.query(SessionTraining).filter(
            SessionTraining.id == exercise_data.training_id,
            SessionTraining.session_id == session_id
        ).first()
    else:
        training = None
    
    if not training:
        return None
    
    # Создаем упражнение в зависимости от типа пользователя
    if user_id > 0:
        db_exercise = Exercise(
            training_id=exercise_data.training_id,
            name=exercise_data.name,
            notes=exercise_data.notes
        )
    elif user_id == 0 and session_id:
        db_exercise = SessionExercise(
            session_id=session_id,
            training_id=exercise_data.training_id,
            name=exercise_data.name,
            notes=exercise_data.notes
        )
    else:
        return None
    
    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)
    
    return db_exercise


def update_exercise(db: Session, exercise_id: int, exercise_data: ExerciseUpdate, user_id: int, session_id: Optional[str] = None) -> Optional[Union[Exercise, SessionExercise]]:
    """Обновить упражнение"""
    exercise = get_exercise_by_id(db, exercise_id, user_id, session_id)
    if not exercise:
        return None
    
    # Преобразуем Pydantic модель в словарь (исключая None)
    update_data = exercise_data.model_dump(exclude_unset=True)
    
    # Обновляем атрибуты
    for key, value in update_data.items():
        if hasattr(exercise, key):
            setattr(exercise, key, value)
    
    db.commit()
    db.refresh(exercise)
    
    return exercise


def delete_exercise(db: Session, exercise_id: int, user_id: int, session_id: Optional[str] = None) -> bool:
    """Удалить упражнение"""
    exercise = get_exercise_by_id(db, exercise_id, user_id, session_id)
    if not exercise:
        return False
    
    db.delete(exercise)
    db.commit()
    return True


def is_exercise_training_owner(db: Session, exercise_id: int, user_id: int, session_id: Optional[str] = None) -> bool:
    """Проверить, является ли пользователь владельцем тренировки, к которой относится упражнение"""
    exercise = get_exercise_by_id(db, exercise_id, user_id, session_id)
    if not exercise:
        return False
    
    if user_id > 0:
        # Для зарегистрированного пользователя проверяем обычную тренировку
        training = db.query(Training).filter(Training.id == exercise.training_id).first()
        if not training:
            return False
        # Явно приводим к bool
        return bool(training.user_id == user_id)
    elif user_id == 0 and session_id:
        # Для гостевого пользователя проверяем сессионную тренировку
        training = db.query(SessionTraining).filter(
            SessionTraining.id == exercise.training_id,
            SessionTraining.session_id == session_id
        ).first()
        return training is not None
    else:
        return False