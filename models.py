from sqlmodel import Field, SQLModel
from pydantic import EmailStr
from datetime import datetime
from sqlalchemy import Column, DateTime, func, UniqueConstraint

class FavoriteFood(SQLModel, table=True):
    user_id: int = Field(foreign_key="users.id", primary_key=True, index=True)
    food_id: int = Field(foreign_key="foods.id", primary_key=True, index=True)
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )

class Users(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: EmailStr = Field(index=True, unique=True)
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
    user_name: str = Field(index=True, unique=True)

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
    user_id: int = Field(foreign_key="users.id", index=True)



class Comments(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    food_id: int = Field(foreign_key="foods.id", index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    text: str
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now()
        )
    )

class FoodLikes(SQLModel, table=True):
    food_id: int = Field(foreign_key="foods.id", primary_key=True, index=True)
    user_id: int = Field(foreign_key="users.id", primary_key=True, index=True)
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now()
        )
    )

class UserFollow(SQLModel, table=True):
    # id: int | None = Field(default=None, primary_key=True)
    follower_id: int = Field(foreign_key="users.id", primary_key=True, index=True)
    following_id: int = Field(foreign_key="users.id", primary_key=True, index=True)
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now()
        )
    )

