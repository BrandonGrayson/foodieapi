from typing import Union

from fastapi import FastAPI
import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from pydantic import BaseModel
import time
from fastapi import HTTPException, status
from schemas import FoodBase, UserBase, FoodCreate

app = FastAPI()

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
def add_user(user: UserBase):
    cur.execute("INSERT INTO users (email, password) VALUES (%s, %s) RETURNING *",
            (user.email, user.password))
    new_user = cur.fetchone()

    conn.commit()
    return new_user

@app.get('/users/{id}', status_code=200)
def get_users(id: int):
    cur.execute(t"SELECT * FROM users")
    users = cur.fetchall()
    if users == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id: {id} was not found")
    return {"users": users}

@app.post("/foods", status_code=201, response_model=FoodCreate)
def add_food(food: FoodBase):
    cur.execute("INSERT INTO foods (description, location, grade, type, image, name) VALUES (%s, %s, %s, %s, %s, %s) RETURNING *",
                (food.description, food.location, food.grade, food.type, food.image, food.name))
    new_food = cur.fetchone()

    conn.commit()
    return new_food

@app.get('/foods/{id}', status_code=200)
def get_foods(id: str):
    cur.execute("SELECT * FROM foods WHERE id = %s", (str(id), ))
    foods = cur.fetchone()

    if foods == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="food with an id: {id} was not found")

    return foods


