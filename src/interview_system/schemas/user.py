# src/interview_system/schemas/user.py

from pydantic import BaseModel, EmailStr
from uuid import UUID

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr

class Config:
    orm_mode = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

