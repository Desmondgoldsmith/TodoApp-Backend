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

connection_successful = False

while not connection_successful:
    try:
        conn = psycopg.connect(
            host='localhost',
            dbname='TodosDB',
            user='postgres',
            password='DessyAdmin',
            port='5432',
            row_factory=dict_row
        )
        cursor = conn.cursor()
        print("Database connection successful")
        connection_successful = True
    except Exception as error:
        print(f"An error occurred: {error}")
        print("Retrying in 2 seconds...")
        time.sleep(2)


# test api
@app.get('/hello')
def HelloWorld():
    return {"data": "Hello World !"}

# endpoint to get all todos
@app.get('/todos', response_model = List[schema.ResponseSchema])
def getTodos(db:Session = Depends(get_db)):
    todoData = db.query(models.Todos).all()
    return todoData

# create a todo
@app.post('/create_todo', status_coude = status.HTTP_201_CREATED, response_model = schema.ResponseSchema)
def CreateTodo(Todo:schema.InputSchema, db: Session = Depends(get_db)):
    todoData = models.Todos(**Todo.model_dump())
    db.add(todoData)
    db.commit()
    db.refresh(todoData)
    return {"status": "success!"
            "data": todoData  
           }