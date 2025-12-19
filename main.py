from typing import Annotated
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI
from psycopg.rows import dict_row
from pydantic import BaseModel
from fastapi import HTTPException, status
import schemas
from models import Users, UserCreate, UserRead, FoodRead, Foods
from pwdlib import PasswordHash
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Session, SQLModel, create_engine, select

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

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

class Token(BaseModel):
    access_token: str
    token_type: str

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

    hashed_password = hash(user.password)

    db_user = Users(email=user.email, password=hashed_password)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user

@app.get('/users/{id}', status_code=200, response_model=UserRead)
def get_user(id: int, session: SessionDep):
    
    statement = select(Users).where(Users.id == id)
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food not found")

    return food

@app.post("/login")
def login(user_credentials: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep):

   statement = select(Users).where(Users.email == user_credentials.username)
   user = session.exec(statement).first()

   if not user:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Credentials")
   
   if not verify_password(user_credentials.password, user.password):
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Credentials")
   
   access_token = create_access_token(data = {"user_id": user.id})
   
   return {"access_token": access_token, "token_type": "bearer"}

# @app.post("/token")
# async def login_for_access_token(
#     form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
# ) -> Token:
#     user = authenticate_user(fake_users_db, form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": user.username}, expires_delta=access_token_expires
#     )


