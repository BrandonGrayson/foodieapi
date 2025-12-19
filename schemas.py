from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    password: str

    class Config:
        from_attributes = True

# class User(UserBase):
#     hashed_password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class FoodBase(BaseModel):
    name: str
    description: str
    location: str
    grade: int
    type: str
    image: str  

class FoodCreate(FoodBase):
    pass

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

    class Config:
        from_attributes = True

class TokenData(BaseModel):
    id: Optional[str] = None
