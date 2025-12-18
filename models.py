from sqlmodel import Field, SQLModel
from pydantic import EmailStr
from datetime import datetime
from sqlalchemy import Column, DateTime, func

class UserCreate(SQLModel):
    email: EmailStr
    password: str

class UserRead(SQLModel):
    id: int
    email: EmailStr
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

class Foods(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: str
    location: str
    type: str
    grade: int
    created_at: datetime
    image: str
    user_id: int = Field(default=None, foreign_key="user.id")