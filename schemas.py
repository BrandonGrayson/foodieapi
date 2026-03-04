from pydantic import BaseModel, EmailStr, computed_field
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel
from config import settings

class UserFollowersRead(SQLModel):
    following_id: int
    follower_id: int
    created_at: datetime

class UserCreate(SQLModel):
    email: EmailStr
    password: str
    full_name: str
    phone_number: str
    user_name: str

class UserRead(SQLModel):
    id: int
    email: EmailStr
    user_name: str
    created_at: datetime
    full_name: str

class FoodRead(SQLModel):
    id: int 
    name: str
    description: str
    location: str
    type: str
    grade: int
    image_key: str
    user_id: int 
    created_at: datetime 

    @computed_field
    @property
    def url(self) -> str:
        return f"https://{settings.AWS_S3_BUCKET_NAME}.s3.amazonaws.com/{self.image_key}"

    class Config:
        from_attributes = True

class UserFollowResponse(SQLModel):
    # id: int
    follower_id: int
    following_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class FavoritesResponse(SQLModel):
    food_id: int 
    user_id: int 
    created_at: datetime 

    class Config:
        from_attributes = True

class FoodLikesResponse(SQLModel):
    # id: int 
    food_id: int 
    user_id: int 
    created_at: datetime 

    class Config:
        from_attributes = True

class CommentCreate(SQLModel):
    text: str = Field(min_length=1, max_length=500)

class CommentRead(SQLModel):
    # id: int
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

