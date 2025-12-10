from pydantic import BaseModel

class FoodRes(BaseModel):
    name: str
    description: str
    location: str
    grade: int
    type: str
    image: str 

    class Config:
        from_attributes = True