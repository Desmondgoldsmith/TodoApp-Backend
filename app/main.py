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
@app.post('/create_todo', status_code = status.HTTP_201_CREATED, response_model = schema.ResponseSchema)
def CreateTodo(Todo:schema.TodoCreate, db: Session = Depends(get_db)):
    todoData = models.Todos(**Todo.model_dump())
    db.add(todoData)
    db.commit()
    db.refresh(todoData)
    return todoData 

# update todo
@app.put('/update_todo/{id}', status_code=status.HTTP_201_CREATED, response_model = schema.ResponseSchema)
def updateTodo(Todo: schema.TodoCreate, db: Session = Depends(get_db)):
    todoData = db.query(models.Todos).filter(models.Todos.id == id)
    data = todoData.first()
    
    # Check if the post exists
    if data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with id {id} not found")
    
    todoData.update(Todo.model_dump(), synchronize_session = False)
    db.commit()
    db.refresh(data)
    
    return data

# delete a todo
@app.delete('/delete_todo/{id}')
def deleteTodo(Todo: schema.TodoCreate, db: Session = Depends(get_db)):
    deleteTodo = db.query(models.Todos).filter(models.Todos.id == id)
    if deleteTodo.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Post with id {id} not found")
    deleteTodo.delete(synchronize_session = False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)   

# get one todo
@app.get('todo/{id}', response_model= schema.ResponseSchema)
def getOneTodo(id:int, db: Session = Depends(get_db)):
    data = db.query(models.Todos).filter(models.Todos.id == id).first()
    
    # Check if the post exists
    if data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with id {id} not found")
    return data