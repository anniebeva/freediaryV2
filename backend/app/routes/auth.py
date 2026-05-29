from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.models.models import User
from app.core.dependencies import get_current_user
from app.core.security import create_access_token, verify_password
from app.crud.user import create_user, get_user_by_email, get_user_by_username
from app.database import get_db
from app.schemas.user import Token, UserCreate, UserLogin, UserResponse
from app.bot.notifications import notify_login

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    # Проверяем, существует ли пользователь с таким email
    if get_user_by_email(db, user_data.email) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )
    
    # Проверяем, существует ли пользователь с таким username
    if get_user_by_username(db, user_data.username) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username already exists",
        )
    
    try:
        return create_user(db, user_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/login", response_model=Token)
def login(
    credentials: UserLogin,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    user = get_user_by_email(db, credentials.email)
    
    if user is None or not verify_password(credentials.password, str(user.password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(subject=str(user.id))
    
    # Send Telegram notification in background if enabled
    telegram_id = getattr(user, 'telegram_id', None)
    notifications_enabled = getattr(user, 'telegram_notifications_enabled', False)
    
    if telegram_id and notifications_enabled:
        background_tasks.add_task(notify_login, user.id)  # type: ignore
    
    return Token(access_token=access_token)


@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user