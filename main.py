from typing import Union, Annotated
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI
import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from pydantic import BaseModel
import time
from fastapi import HTTPException, status
from schemas import FoodBase, UserBase, FoodCreate, User, UserOut
from pwdlib import PasswordHash
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select
from pydantic import BaseModel, EmailStr

app = FastAPI()

class foods(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: str
    location: str
    type: str
    grade: int
    created_at: datetime
    image: str
    user_id: int = Field(default=None, foreign_key="user.id")

class users(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: EmailStr
    password: str

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

while True:
    try:
        conn = psycopg.connect(host="localhost", dbname="foodie", user='postgres', password='Prolific1',  row_factory=dict_row) 
        cur= conn.cursor() 
        print('database connection successful')
        break

    except Exception as e:
        print('Connection error', e)
        time.sleep(2)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/users", status_code=201)
def add_user(user: User, session: SessionDep):

    session.add(user)
    session.commit()
    session.refresh(user)

    # hashed_password = hash(user.password)
    # cur.execute("INSERT INTO users (email, password) VALUES (%s, %s) RETURNING *",
    #         (user.email, hashed_password ))
    # new_user = cur.fetchone()

    # conn.commit()
    return user

@app.get('/users/{id}', status_code=200, response_model=UserOut)
def get_user(id: int, session: SessionDep):
    cur.execute("SELECT * FROM users WHERE id = %s", (str(id), ))
    user = cur.fetchone()
    if user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id: {id} was not found")
    return user

@app.post("/foods", status_code=201, response_model=FoodCreate)
def add_food(food: FoodBase, session: SessionDep):
    cur.execute("INSERT INTO foods (description, location, grade, type, image, name) VALUES (%s, %s, %s, %s, %s, %s) RETURNING *",
                (food.description, food.location, food.grade, food.type, food.image, food.name))
    new_food = cur.fetchone()

    conn.commit()
    return new_food

@app.get('/foods/{id}', status_code=200)
def get_foods(id: str, session: SessionDep):
    cur.execute("SELECT * FROM foods WHERE id = %s", (str(id), ))
    foods = cur.fetchone()

    if foods == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="food with an id: {id} was not found")

    return foods


