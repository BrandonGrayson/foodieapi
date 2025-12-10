from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    password: str


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