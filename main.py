from typing import Annotated
from fastapi import FastAPI
from fastapi import HTTPException, status
from models import Users, UserCreate, UserRead, FoodRead, Foods
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends, FastAPI, HTTPException, Cookie, Response
from sqlmodel import Session, SQLModel, create_engine, select
import schemas
import oauth
import utils
from config import settings
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
#token: str = Depends(oauth.oauth2_scheme)
def get_current_user(access_token: str | None = Cookie(default=None)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    if access_token is None:
        raise credentials_exception

    return oauth.verify_access_token(access_token, credentials_exception)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/users", status_code=201, response_model=UserRead)
def add_user(user: UserCreate, session: SessionDep):

    hashed_password = utils.hash(user.password)

    db_user = Users(email=user.email, password=hashed_password, phone_number=user.phone_number, full_name=user.full_name,  user_name=user.user_name)

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

@app.post("/login")
def login(user_credentials: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep):
   
   print('user creds', user_credentials)

   statement = select(Users).where(Users.email == user_credentials.username)
   user = session.exec(statement).first()

   if not user:
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
   
   if not utils.verify_password(user_credentials.password, user.password):
       raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
   
   access_token = oauth.create_access_token(data = {"user_id": user.id})

   response = RedirectResponse(
        url="http://localhost:3000/profile",
        status_code=303,
    )
   
   response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,          # true in production
        samesite="lax",       # or "strict"
        max_age=60 * 30
    )
   
   return response

@app.get("/me", response_model=UserRead)
def read_me(
    session: SessionDep,
    user_id: int = Depends(get_current_user)
):
    user = session.get(Users, user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
