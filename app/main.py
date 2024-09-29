from fastapi import FastAPI, Response,status, HTTPException, Depends
import psycopg
from psycopg.rows import dict_row
from sqlalchemy.orm import Session
from .database import engine, get_db
from . import models, schema
from typing import List
import time

models.Base.metadata.create_all(bind=engine)


app = FastAPI()


# test api
@app.get('/hello')
def HelloWorld():
    return {"data": "Hello World !"}

# endpoint to get all todos
@app.get('/todos')
def getTodos():
    return {"status": "successful"
           }