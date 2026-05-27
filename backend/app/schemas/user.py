from pydantic import BaseModel, Field, validator
from app.models.models import UserRole


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    
    @validator('password')
    def validate_password_length(cls, v):
        char_length = len(v)
        
        if char_length < 6:
            raise ValueError(f'Пароль должен содержать минимум 6 символов. Текущая длина: {char_length} символов.')
        
        return v


class UserLogin(BaseModel):
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(..., min_length=6)


class UserResponse(UserBase):
    id: int
    role: UserRole = UserRole.USER

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
