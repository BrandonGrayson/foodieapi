# NOTES & Bugs: 
# update 

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
import boto3
import uuid
from fastapi import UploadFile, File
import models

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


@app.get("/foods/likes/{food_id}", response_model=list[schemas.FoodLikesResponse])
def get_food_Likes(food_id: int, session: SessionDep):

    statement = select(models.FoodLikes).where(models.FoodLikes.food_id == food_id)
    food_Likes = session.exec(statement).all()

    return food_Likes

@app.post("/foods/{food_id}/like", status_code=201, response_model=schemas.FoodLikesResponse)
def add_food_Likes(food_id: int, session: SessionDep, user_id: int = Depends(get_current_user)):

    food = session.get(Foods, food_id)

    if not food:
        raise HTTPException(404, "Food not found")
    
    existing = session.exec(
        select(models.FoodLikes).where(models.FoodLikes.food_id == food_id, models.FoodLikes.user_id == user_id)
    ).first()

    if existing:
        raise HTTPException(409, "Already liked")

    food_likes = models.FoodLikes(food_id=food_id, user_id=user_id)

    session.add(food_likes)
    session.commit()
    session.refresh(food_likes)

    return food_likes

@app.get("/foods/{food_id}/comments", response_model=list[schemas.CommentRead])
def get_comments(food_id: int, session: SessionDep, limit: int = 20, offset: int = 0):

    food = session.get(Foods, food_id)
    if not food:
        raise HTTPException(404, "Food not found")

    statement = select(models.Comments).where(models.Comments.food_id == food_id).order_by(models.Comments.created_at.desc()).limit(limit).offset(offset)
    comments = session.exec(statement).all()

    return comments

@app.post('/uploadfood')
async def upload_food_items(user_id: int = Depends(get_current_user), file: UploadFile = File()):

    print("AWS_ACCESS_KEY_ID:", settings.AWS_ACCESS_KEY_ID)
    print("AWS_SECRET_ACCESS_KEY:", settings.AWS_SECRET_ACCESS_KEY)
    print("AWS_REGION:", settings.AWS_REGION)

    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "Only images allowed")
    
    contents = await file.read()

    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(400, "File too large")

    s3 = boto3.client(
        "s3",
    region_name=settings.AWS_REGION,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )

    ext = file.filename.split(".")[-1]
    key = f"users/{user_id}/{uuid.uuid4()}.{ext}"

    s3.put_object(
    Bucket=settings.AWS_S3_BUCKET_NAME,
    Key=key,
    Body=contents,
    ContentType=file.content_type
)
    
    return {
        "key": key,
        "url": f"https://{settings.AWS_S3_BUCKET_NAME}.s3.amazonaws.com/{key}"
    }


@app.get('/listfoodieitems', response_model=list[schemas.FoodResponse])
def get_all_food_items(session: SessionDep, user_id: int = Depends(get_current_user)):

    print("AWS_ACCESS_KEY_ID:", settings.AWS_ACCESS_KEY_ID)
    print("AWS_SECRET_ACCESS_KEY:", settings.AWS_SECRET_ACCESS_KEY)
    print("AWS_REGION:", settings.AWS_REGION)
    s3 = boto3.client(
        "s3",
    region_name=settings.AWS_REGION,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
    
    prefix = f"users/{user_id}/"

    bucket_name = settings.AWS_S3_BUCKET_NAME

    paginator = s3.get_paginator("list_objects_v2")

    objects = []

    for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
        for obj in page.get("Contents", []):
            signed_url = s3.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": settings.AWS_S3_BUCKET_NAME,
                    "Key": obj["Key"],
                },
                ExpiresIn=3600,  # 1 hour
            )
            objects.append({
                "key": obj["Key"],
                "url": signed_url,
                "size": obj["Size"],
                "last_modified": obj["LastModified"].isoformat(),
            })

    statement = select(Foods).where(Foods.user_id == user_id)
    foods = session.exec(statement).all()

    object_lookup = {obj["key"]: obj for obj in objects}
    foods_and_key = [
        {
            **food.model_dump(),
            "url": object_lookup[food.image_key]["url"],
            "image_key": object_lookup[food.image_key]["key"]
        }
        for food in foods
        if food.image_key in object_lookup
    ]

    return foods_and_key

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
def login(user_credentials: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep, response: Response):
   

   print('user creds', user_credentials)

   statement = select(Users).where(Users.email == user_credentials.username)
   user = session.exec(statement).first()

   if not user:
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
   
   if not utils.verify_password(user_credentials.password, user.password):
       raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
   
   access_token = oauth.create_access_token(data = {"user_id": user.id})

   print('accessToken---->', access_token)
   
   response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,   
        samesite="lax",   
        max_age=60 * 30,
        path="/"
    )
   
   return {"message": "Login successful"}

@app.get("/me", response_model=UserRead)
def read_me(
    session: SessionDep,
    user_id: int = Depends(get_current_user)
):
    user = session.get(Users, user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
