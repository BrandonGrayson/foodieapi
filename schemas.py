from pydantic import BaseModel, EmailStr
from datetime import datetime
from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    email: EmailStr
    password: str

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


