from typing import Annotated
from fastapi import FastAPI
from fastapi import HTTPException, status
from models import Users, UserCreate, UserRead, FoodRead, Foods
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Session, SQLModel, create_engine, select
import schemas
import oauth
import utils
from config import settings

app = FastAPI()

# SQLMODEL_DATABASE_URL = "postgresql+psycopg://postgres:Prolific1@localhost:/foodie"
SQLMODEL_DATABASE_URL = f"postgresql+psycopg://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"

engine = create_engine(SQLMODEL_DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# session = Session(engine)
def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

def get_current_user(token: str = Depends(oauth.oauth2_scheme)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    return oauth.verify_access_token(token, credentials_exception)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/users", status_code=201, response_model=UserRead)
def add_user(user: UserCreate, session: SessionDep, user_id: int = Depends(get_current_user)):

    hashed_password = utils.hash(user.password)

    db_user = Users(email=user.email, password=hashed_password)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user

@app.get('/users/{id}', status_code=200, response_model=UserRead)
def get_user(id: int, session: SessionDep, user_id: int = Depends(get_current_user)):
    
    statement = select(Users).where(Users.id == id)
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user
    

@app.post("/foods", status_code=201, response_model=FoodRead)
def add_food(food: schemas.FoodCreate, session: SessionDep, user_id: int = Depends(get_current_user)):

    print(user_id)

    db_Foods = Foods(**food.model_dump(), user_id=user_id)

    session.add(db_Foods)
    session.commit()
    session.refresh(db_Foods)

    return db_Foods

@app.get('/foods/{id}', status_code=200, response_model=FoodRead)
def get_foods(id: int, session: SessionDep, user_id: int = Depends(get_current_user)):

    statement = select(Foods).where(Foods.id == id)
    food = session.exec(statement).first()

    if not food:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food not found")

    return food

@app.delete("/foods/{id}", response_model=schemas.FoodCreate)
def delete_food(id: int, session: SessionDep, user_id: int = Depends(get_current_user)):

    statement = select(Foods).where(Foods.id == id)
    food = session.exec(statement).one()

    session.delete(food)
    session.commit()

    return food


@app.post("/login", response_model=schemas.Token)
def login(user_credentials: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep):

   statement = select(Users).where(Users.email == user_credentials.username)
   user = session.exec(statement).first()

   if not user:
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
   
   if not utils.verify_password(user_credentials.password, user.password):
       raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
   
   access_token = oauth.create_access_token(data = {"user_id": user.id})
   
   return {"access_token": access_token, "token_type": "bearer"}



