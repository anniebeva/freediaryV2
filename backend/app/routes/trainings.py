from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.crud.training import (
    create_training,
    delete_training,
    get_training_by_id,
    get_trainings,
    is_training_owner,
    update_training,
)
from app.crud.exercise import get_exercises_by_training_id
from app.schemas.training import TrainingCreate, TrainingResponse, TrainingUpdate, TrainingWithExercises
from app.models.models import User, UserRole

router = APIRouter(prefix="/trainings", tags=["trainings"])

def get_user_role(current_user: User) -> str:
    """Получить роль пользователя в виде строки"""
    if not current_user:
        return "guest"
    user_role = str(current_user.role) if hasattr(current_user, 'role') else "user"
    return user_role


def format_training_response(training):
    """Преобразует объект Training или SessionTraining в словарь для ответа"""
    # Получаем JSON поля (в БД они хранятся как pool_training, depth_training, gym_training)
    pool_training = getattr(training, 'pool_training', None) or getattr(training, 'poolTraining', None)
    depth_training = getattr(training, 'depth_training', None) or getattr(training, 'depthTraining', None)
    gym_training = getattr(training, 'gym_training', None) or getattr(training, 'gymTraining', None)
    
    # Получаем user_id (у SessionTraining этого поля нет, поэтому default=0)
    user_id = getattr(training, 'user_id', 0)
    
    return {
        "id": training.id,
        "type": training.type,
        "date": training.date,
        "difficulty": training.difficulty,
        "notes": training.notes,
        "poolTraining": pool_training,
        "depthTraining": depth_training,
        "gymTraining": gym_training,
        "user_id": user_id,
    }


@router.post("/", response_model=TrainingResponse, status_code=status.HTTP_201_CREATED)
def create_my_training(
    training_data: TrainingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID")
):
    user_id = getattr(current_user, 'id', 0) if current_user else 0
    training = create_training(db, training_data, user_id, x_session_id)
    
    if training is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Training was not created",
        )
    
    return format_training_response(training)


@router.get("/", response_model=List[TrainingResponse])
def get_my_trainings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID")
):
    user_id = getattr(current_user, 'id', 0) if current_user else 0
    trainings = get_trainings(db, user_id, x_session_id)
    
    return [format_training_response(training) for training in trainings]


@router.get("/{training_id}", response_model=TrainingWithExercises)
def get_my_training(
    training_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID")
):
    user_id = getattr(current_user, 'id', 0) if current_user else 0
    training = get_training_by_id(db, training_id, user_id, x_session_id)
    
    if training is None:
        raise HTTPException(status_code=404, detail="Training not found")
    
    exercises = get_exercises_by_training_id(db, training_id, user_id, x_session_id)
    
    return {
        **format_training_response(training),
        "exercises": exercises
    }


@router.put("/{training_id}", response_model=TrainingResponse)
def update_my_training(
    training_id: int,
    training_data: TrainingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID")
):
    user_id = getattr(current_user, 'id', 0) if current_user else 0
    
    if not is_training_owner(db, training_id, user_id, x_session_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this training",
        )
    
    updated_training = update_training(db, training_id, training_data, user_id, x_session_id)
    
    if updated_training is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Training was not updated",
        )
    
    return format_training_response(updated_training)


@router.delete("/{training_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_training(
    training_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID")
):
    user_id = getattr(current_user, 'id', 0) if current_user else 0
    
    if not is_training_owner(db, training_id, user_id, x_session_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this training",
        )
    
    if not delete_training(db, training_id, user_id, x_session_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training not found",
        )
    
    return None