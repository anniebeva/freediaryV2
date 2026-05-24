from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text, JSON, Enum, DateTime
from sqlalchemy.orm import relationship
import enum
from datetime import date, datetime, timedelta

from app.database import Base

class TrainingType(enum.Enum):
    Pool = "Pool"
    Depth = "Depth"
    Gym = "Gym"
    Other = "Other"

class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(200), nullable=False)  # Храним хэш пароля
    
    # Связи
    trainings = relationship("Training", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"

class Training(Base):
    """Модель тренировки (для зарегистрированных пользователей)"""
    __tablename__ = "trainings"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(Enum(TrainingType), nullable=False)
    date = Column(Date, nullable=False)
    difficulty = Column(Integer, nullable=False)  # 1-5
    notes = Column(Text, nullable=True)
    
    # JSON поля для дополнительных данных (snake_case в БД)
    pool_training = Column(JSON, nullable=True)  # JSON для полей poolTraining
    depth_training = Column(JSON, nullable=True)  # JSON для полей depthTraining
    gym_training = Column(JSON, nullable=True)   # JSON для полей gymTraining
    
    # Свойства для camelCase доступа в коде
    @property
    def poolTraining(self):
        return self.pool_training
    
    @poolTraining.setter
    def poolTraining(self, value):
        self.pool_training = value
    
    @property
    def depthTraining(self):
        return self.depth_training
    
    @depthTraining.setter
    def depthTraining(self, value):
        self.depth_training = value
    
    @property
    def gymTraining(self):
        return self.gym_training
    
    @gymTraining.setter
    def gymTraining(self, value):
        self.gym_training = value
    
    # Связи
    user = relationship("User", back_populates="trainings")
    exercises = relationship("Exercise", back_populates="training", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Training(id={self.id}, user_id={self.user_id}, type={self.type}, date={self.date})>"

class Exercise(Base):
    """Модель упражнения (для зарегистрированных пользователей)"""
    __tablename__ = "exercises"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    training_id = Column(Integer, ForeignKey("trainings.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    notes = Column(Text, nullable=True)
    
    # Связи
    training = relationship("Training", back_populates="exercises")
    
    def __repr__(self):
        return f"<Exercise(id={self.id}, training_id={self.training_id}, name={self.name})>"

class SessionTracking(Base):
    """Модель для отслеживания сессий"""
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(64), unique=True, nullable=False, index=True)  # Идентификатор сессии
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)  # Время истечения сессии (24 часа)
    last_accessed = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Связи с сессионными тренировками
    session_trainings = relationship("SessionTraining", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SessionTracking(session_id={self.session_id}, expires_at={self.expires_at})>"

class SessionTraining(Base):
    """Модель тренировки для гостевых пользователей (сессионные данные)"""
    __tablename__ = "session_trainings"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(64), ForeignKey("sessions.session_id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(Enum(TrainingType), nullable=False)
    date = Column(Date, nullable=False)
    difficulty = Column(Integer, nullable=False)  # 1-5
    notes = Column(Text, nullable=True)
    
    # JSON поля для дополнительных данных (snake_case в БД)
    pool_training = Column(JSON, nullable=True)
    depth_training = Column(JSON, nullable=True)
    gym_training = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Свойства для camelCase доступа в коде
    @property
    def poolTraining(self):
        return self.pool_training
    
    @poolTraining.setter
    def poolTraining(self, value):
        self.pool_training = value
    
    @property
    def depthTraining(self):
        return self.depth_training
    
    @depthTraining.setter
    def depthTraining(self, value):
        self.depth_training = value
    
    @property
    def gymTraining(self):
        return self.gym_training
    
    @gymTraining.setter
    def gymTraining(self, value):
        self.gym_training = value
    
    # Связи
    session = relationship("SessionTracking", back_populates="session_trainings")
    session_exercises = relationship("SessionExercise", back_populates="session_training", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SessionTraining(id={self.id}, session_id={self.session_id}, type={self.type}, date={self.date})>"

class SessionExercise(Base):
    """Модель упражнения для гостевых пользователей (сессионные данные)"""
    __tablename__ = "session_exercises"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(64), ForeignKey("sessions.session_id", ondelete="CASCADE"), nullable=False, index=True)
    training_id = Column(Integer, nullable=False)  # ID сессионной тренировки
    name = Column(String(100), nullable=False)
    notes = Column(Text, nullable=True)
    
    # Связи
    session = relationship("SessionTracking")
    session_training = relationship("SessionTraining", back_populates="session_exercises")
    
    def __repr__(self):
        return f"<SessionExercise(id={self.id}, session_id={self.session_id}, training_id={self.training_id}, name={self.name})>"
