from typing import List, Optional

import app.models.memory_storage as storage
from app.models.memory_storage import Exercise
from app.schemas.exercise import ExerciseCreate, ExerciseUpdate
from app.crud.training import get_training_by_id


def get_exercises() -> List[Exercise]:
    return list(storage.exercises_db.values())


def get_exercise_by_id(exercise_id: int) -> Optional[Exercise]:
    return storage.exercises_db.get(exercise_id)


def get_exercises_by_training_id(training_id: int, session_id: Optional[str] = None) -> List[Exercise]:
    exercises = []
    
    # 1. Ищем в общем хранилище
    for exercise in storage.exercises_db.values():
        if exercise.training_id == training_id:
            exercises.append(exercise)
    
    # 2. Если есть session_id, ищем в сессии
    if session_id:
        session = storage.sessions_db.get(session_id)
        if session:
            for exercise in session.exercises.values():
                if exercise.training_id == training_id:
                    exercises.append(exercise)
    
    return exercises

def create_exercise(exercise_data: ExerciseCreate, session_id: Optional[str] = None) -> Optional[Exercise]:
    # Проверяем существование тренировки
    training = get_training_by_id(exercise_data.training_id, session_id)
    if training is None:
        return None

    # Создаём упражнение
    exercise = Exercise(
        training_id=exercise_data.training_id,
        name=exercise_data.name,
        notes=exercise_data.notes
    )
    
    # Сохраняем в зависимости от типа пользователя
    if session_id and training.user_id == 0:
        session = storage.sessions_db.get(session_id)
        if session is None:
            return None
        session.exercise_counter += 1
        exercise.id = session.exercise_counter
        session.exercises[exercise.id] = exercise
    else:
        storage.exercise_counter += 1
        exercise.id = storage.exercise_counter
        storage.exercises_db[exercise.id] = exercise
    
    return exercise

def delete_exercise(exercise_id: int) -> bool:
    if exercise_id not in storage.exercises_db:
        return False

    del storage.exercises_db[exercise_id]

    return True

def update_exercise(exercise_id: int, exercise_data: ExerciseUpdate, session_id: Optional[str] = None) -> Optional[Exercise]:
    # Ищем упражнение
    exercise = storage.exercises_db.get(exercise_id)
    
    # Если не нашли в общем хранилище, ищем в сессиях
    if exercise is None and session_id:
        session = storage.sessions_db.get(session_id)
        if session and exercise_id in session.exercises:
            exercise = session.exercises[exercise_id]
    
    if exercise is None:
        return None
    
    # Обновляем только name и notes
    if exercise_data.name is not None:
        exercise.name = exercise_data.name
    if exercise_data.notes is not None:
        exercise.notes = exercise_data.notes
    
    return exercise


def is_exercise_training_owner(exercise_id: int, user_id: int, session_id: Optional[str] = None) -> bool:
    exercise = get_exercise_by_id(exercise_id)
    
    if exercise is None:
        return False
    
    # Ищем тренировку (сначала в trainings_db, потом в сессии)
    training = storage.trainings_db.get(exercise.training_id)
    
    if training is None and session_id:
        session = storage.sessions_db.get(session_id)
        if session and exercise.training_id in session.trainings:
            training = session.trainings[exercise.training_id]
    
    if training is None:
        return False
    
    return training.user_id == user_id