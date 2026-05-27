from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text, JSON, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base


class TrainingType(str, enum.Enum):
    Pool = "Pool"
    Depth = "Depth"
    Gym = "Gym"
    Other = "Other"


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(200), nullable=False)
    role = Column(String(10), default=UserRole.USER.value, nullable=False)
    
    trainings = relationship("Training", back_populates="user", cascade="all, delete-orphan")


class Training(Base):
    __tablename__ = "trainings"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(20), nullable=False)
    date = Column(Date, nullable=False)
    difficulty = Column(Integer, nullable=False)
    notes = Column(Text, nullable=True)
    pool_training = Column(JSON, nullable=True)
    depth_training = Column(JSON, nullable=True)
    gym_training = Column(JSON, nullable=True)
    
    user = relationship("User", back_populates="trainings")
    exercises = relationship("Exercise", back_populates="training", cascade="all, delete-orphan")


class Exercise(Base):
    __tablename__ = "exercises"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    training_id = Column(Integer, ForeignKey("trainings.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    notes = Column(Text, nullable=True)
    
    training = relationship("Training", back_populates="exercises")


class SessionTracking(Base):
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(64), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    last_accessed = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    session_trainings = relationship("SessionTraining", back_populates="session", cascade="all, delete-orphan")


class SessionTraining(Base):
    __tablename__ = "session_trainings"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(64), ForeignKey("sessions.session_id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(20), nullable=False)
    date = Column(Date, nullable=False)
    difficulty = Column(Integer, nullable=False)
    notes = Column(Text, nullable=True)
    pool_training = Column(JSON, nullable=True)
    depth_training = Column(JSON, nullable=True)
    gym_training = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    session = relationship("SessionTracking", back_populates="session_trainings")
    session_exercises = relationship("SessionExercise", back_populates="session_training", cascade="all, delete-orphan", foreign_keys="SessionExercise.training_id")


class SessionExercise(Base):
    __tablename__ = "session_exercises"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(64), ForeignKey("sessions.session_id", ondelete="CASCADE"), nullable=False, index=True)
    training_id = Column(Integer, ForeignKey("session_trainings.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    notes = Column(Text, nullable=True)
    
    session = relationship("SessionTracking")
    session_training = relationship("SessionTraining", back_populates="session_exercises", foreign_keys=[training_id])