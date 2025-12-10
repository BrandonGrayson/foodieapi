from typing import Union

from fastapi import FastAPI
import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from pydantic import BaseModel
import time

app = FastAPI()

class User(BaseModel):
    username: str
    password: str

class Food(BaseModel):
    name: str
    description: str
    location: str
    grade: int
    type: str
    user_id: str
    image: str  

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
def add_user(user: User):
    cur.execute("INSERT INTO users (username, password) VALUES (%s, %s) RETURNING *",
            (user.username, user.password))
    new_user = cur.fetchone()
    conn.commit()
    return{"users": new_user}

@app.get('/users', status_code=200)
def get_users():
    cur.execute(t"SELECT * FROM users")
    users = cur.fetchall()
    return {"users": users}

@app.post("/foods", status_code=201)
def add_food(food: Food):
    cur.execute("INSERT INTO foods (name, description, location, grade, type, user_id, image) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING *",
                (food.name, food.description, food.location, food.grade, food.type, food.user_id, food.image))
    new_food = cur.fetchone()
    conn.commit()
    return{"users": new_food}

@app.get('/foods/user_id', status_code=200)
def get_foods(user_id: int):
    cur.execute("SELECT * FROM foods WHERE user_id = %s", str((user_id)))
    foods = cur.fetchall()

    return{"foods": foods}


