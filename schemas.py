from pydantic import BaseModel, EmailStr, computed_field, ConfigDict
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel
from config import settings
import boto3


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
        s3 = boto3.client(
            "s3",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

        return s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": settings.AWS_S3_BUCKET_NAME,
                "Key": self.image_key,
            },
            ExpiresIn=3600,  # 1 hour
        )

    model_config = ConfigDict(from_attributes=True)

class UserFollowResponse(SQLModel):
    # id: int
    follower_id: int
    following_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class FavoritesResponse(SQLModel):
    food_id: int 
    user_id: int 
    created_at: datetime 

    model_config = ConfigDict(from_attributes=True)

class FoodLikesResponse(SQLModel):
    # id: int 
    food_id: int 
    user_id: int 
    created_at: datetime 

    model_config = ConfigDict(from_attributes=True)

class CommentCreate(SQLModel):
    text: str = Field(min_length=1, max_length=500)

class CommentRead(SQLModel):
    # id: int
    food_id: int
    user_id: int
    text: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class LoginResponse(BaseModel):
    message: str

class UserBase(BaseModel):
    email: EmailStr
    password: str

    model_config = ConfigDict(from_attributes=True)

class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class FoodBase(BaseModel):
    name: str
    description: str
    location: str
    grade: int
    type: str
    image_key: str

class FoodCreate(FoodBase):
    pass

    model_config = ConfigDict(from_attributes=True)

class FoodResponse(FoodBase):
    id: int
    created_at: datetime
    url: str
    user_id: int

class Token(BaseModel):
    access_token: str
    token_type: str

    model_config = ConfigDict(from_attributes=True)

class TokenData(BaseModel):
    id: Optional[int] = None

