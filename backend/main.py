from fastapi import FastAPI, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db, create_tables
from app.routes.auth import router as auth_router
from app.routes.exercises import router as exercises_router
from app.routes.trainings import router as trainings_router
from app.routes.telegram import router as telegram_router
from app.crud.session_cleanup import cleanup_expired_sessions
from app.core.config import settings
from app.bot.handler import TelegramBotHandler

app = FastAPI()

# Регистрируем глобальный обработчик для ошибок валидации
def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"detail": "Missing or invalid fields", "errors": exc.errors()}
    )

app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Создаём экземпляр бота
bot_handler = TelegramBotHandler()

# Создание таблиц и запуск бота при запуске приложения
@app.on_event("startup")
async def on_startup():
    """Создание таблиц и запуск Telegram бота"""
    print("Создание таблиц базы данных...")
    create_tables()
    print("Таблицы базы данных созданы успешно!")
    
    # Запускаем Telegram бота
    await bot_handler.start_bot()

@app.on_event("shutdown")
async def on_shutdown():
    """Остановка Telegram бота"""
    await bot_handler.stop_bot()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "x-session-id"],
)

app.include_router(auth_router)
app.include_router(trainings_router)
app.include_router(exercises_router)
app.include_router(telegram_router)


@app.get("/")
def read_root():
    return {"message": "Welcome to FreeDiary API"}


@app.get("/health")
def health_check():
    """Проверка работоспособности API"""
    return {"status": "healthy", "database": "SQLite"}


@app.post("/cleanup-sessions")
def cleanup_sessions(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Очистить просроченные сессии
    
    Этот эндпоинт можно вызывать периодически для очистки старых сессий.
    В продакшене рекомендуется настроить cron-задачу.
    """
    def cleanup_task():
        deleted_count = cleanup_expired_sessions(db)
        print(f"Очищено {deleted_count} просроченных сессий")
    
    background_tasks.add_task(cleanup_task)
    return {"message": "Задача очистки сессий запущена в фоновом режиме"}


@app.get("/db-info")
def get_database_info(db: Session = Depends(get_db)):
    """Получить информацию о состоянии базы данных"""
    from app.models.models import User, Training, Exercise, SessionTracking, SessionTraining, SessionExercise
    
    user_count = db.query(User).count()
    training_count = db.query(Training).count()
    exercise_count = db.query(Exercise).count()
    session_count = db.query(SessionTracking).count()
    session_training_count = db.query(SessionTraining).count()
    session_exercise_count = db.query(SessionExercise).count()
    
    return {
        "database": "SQLite",
        "tables": {
            "users": user_count,
            "trainings": training_count,
            "exercises": exercise_count,
            "sessions": session_count,
            "session_trainings": session_training_count,
            "session_exercises": session_exercise_count
        }
    }

# Настройка Swagger для Bearer авторизации
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Freediary API",
        version="1.0.0",
        routes=app.routes,
    )
    
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method.setdefault("security", []).append({"BearerAuth": []})
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)