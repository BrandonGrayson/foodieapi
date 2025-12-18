from typing import Annotated
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI
from psycopg.rows import dict_row
from pydantic import BaseModel
from fastapi import HTTPException, status
from schemas import FoodBase, FoodCreate
from models import Users, UserCreate, UserRead, FoodRead, Foods
from pwdlib import PasswordHash
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select

app = FastAPI()

SQLMODEL_DATABASE_URL = "postgresql+psycopg://postgres:Prolific1@localhost/foodie"

engine = create_engine(SQLMODEL_DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# session = Session(engine)
def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# class UserInDB(User):
#     hashed_password: str

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# def get_user(db, username: str):
#     if username in db:
#         user_dict = db[username]
#         return UserInDB(**user_dict)

# def authenticate_user(fake_db, username: str, password: str):
#     user = get_user(fake_db, username)
#     if not user:
#         return False
#     if not verify_password(password, user.hashed_password):
#         return False
#     return user

#password hashing

def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


def hash(password):
    return password_hash.hash(password)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/users", status_code=201, response_model=UserRead)
def add_user(user: UserCreate, session: SessionDep):

    db_user = Users(**user.model_dump())

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user

@app.get('/users/{id}', status_code=200, response_model=UserRead)
def get_user(id: int, session: SessionDep):
    
    statment = select(Users).where(Users.id == id)
    user = session.exec(statment).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
    

@app.post("/foods", status_code=201, response_model=FoodRead)
def add_food(food: FoodRead, session: SessionDep):

    db_Foods = Foods(**food.model_dump())

    session.add(db_Foods)
    session.commit()
    session.refresh(db_Foods)

    return db_Foods

@app.get('/foods/{id}', status_code=200, response_model=FoodRead)
def get_foods(id: int, session: SessionDep):

    statement = select(Foods).where(Foods.id == id)
    food = session.exec(statement).first()

    if not food:
        raise HTTPException(status_code=404, detail="Food not found")

    return food


