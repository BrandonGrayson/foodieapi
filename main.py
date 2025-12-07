from typing import Union

from fastapi import FastAPI
import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
import time

app = FastAPI()

while True:
    try:
        with psycopg.connect(host="localhost", dbname="foodie", user='postgres', password='Prolific1',  row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                print('database connection successful')
                break

    except Exception as e:
        print('Connection error', e)
        time.sleep(23)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/users/{username}/{password}")
def add_user(username: str, password: str):
    cur.execute(t" INSERT INTO users (username, password) VALUES ({username}), ({password})")
    return{"users": "User"}

