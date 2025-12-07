from typing import Union

from fastapi import FastAPI
import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool


app = FastAPI()

try:
    with psycopg.connect(host="localhost", dbname="foodie", user='postgres', password='Prolific1',  row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            print('database connection successful')

except Exception as e:
    print('Connection error', e)



@app.get("/")
def read_root():
    return {"Hello": "World"}

