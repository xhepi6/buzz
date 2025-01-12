from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID, uuid4

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    nickname: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    nickname: Optional[str] = None
    password: Optional[str] = None

class UserInDB(UserBase):
    id: UUID
    hashed_password: str

class User(UserBase):
    id: UUID
