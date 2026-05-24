from pydantic import BaseModel, Field
from typing import Optional

class ExerciseBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    notes: Optional[str] = Field(None, max_length=500)

class ExerciseCreate(ExerciseBase):
    training_id: int = Field(..., gt=0)

class ExerciseUpdate(ExerciseBase):
    pass

class ExerciseResponse(ExerciseBase):
    id: int
    training_id: int

    class Config:
        from_attributes = True