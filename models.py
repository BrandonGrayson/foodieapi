from sqlmodel import Field, SQLModel
from pydantic import EmailStr
from datetime import datetime
from sqlalchemy import Column, DateTime, func, UniqueConstraint

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

class Users(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: EmailStr
    password: str
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now()
        )
    ) 
    phone_number: str
    full_name: str
    user_name: str

class Foods(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: str
    location: str
    type: str
    grade: int
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now()
        )
    ) 
    image_key: str
    user_id: int = Field(default=None, foreign_key="users.id")

class FoodRead(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: str
    location: str
    type: str
    grade: int
    image_key: str
    user_id: int = Field(default=None, foreign_key="user.id")
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now()
        )
    ) 

class Comments(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    food_id: int = Field(foreign_key="foods.id")
    user_id: int = Field(foreign_key="users.id")
    text: str
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now()
        )
    )

class FoodLikes(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    food_id: int = Field(foreign_key="foods.id")
    user_id: int = Field(foreign_key="users.id")
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now()
        )
    )
    __table_args__ = (
        UniqueConstraint("food_id", "user_id"),
    )

