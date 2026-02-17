from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel

class UserFollowResponse(SQLModel):
    id: int
    follower_id: int
    following_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class FoodLikesResponse(SQLModel):
    id: int 
    food_id: int 
    user_id: int 
    created_at: datetime 

    class Config:
        from_attributes = True

class CommentCreate(SQLModel):
    text: str = Field(min_length=1, max_length=500)

class CommentRead(SQLModel):
    id: int
    food_id: int
    user_id: int
    text: str
    created_at: datetime

    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    message: str

class UserBase(BaseModel):
    email: EmailStr
    password: str

    class Config:
        from_attributes = True

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
    image_key: str

class FoodCreate(FoodBase):
    pass

    class Config:
        from_attributes = True

class FoodResponse(FoodBase):
    id: int
    created_at: datetime
    url: str
    user_id: int

class Token(BaseModel):
    access_token: str
    token_type: str

    class Config:
        from_attributes = True

class TokenData(BaseModel):
    id: Optional[int] = None

