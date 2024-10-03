from fastapi import FastAPI, Response, status, HTTPException, Depends
import psycopg
from psycopg.rows import dict_row
from sqlalchemy.orm import Session
from .database import engine, get_db, DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT
from . import models, schema
from typing import List
import time
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
from .redis_config import init_redis
import asyncio

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

connection_successful = False

while not connection_successful:
    try:
        conn = psycopg.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            row_factory=dict_row
        )
        cursor = conn.cursor()
        print("Database connection successful")
        connection_successful = True
    except Exception as error:
        print(f"An error occurred: {error}")
        print("Retrying in 2 seconds...")
        time.sleep(2)

@app.on_event("startup")
async def startup_event():
    await init_redis(app)

@app.get('/hello')
def HelloWorld():
    return {"data": "Hello World !"}

@app.get('/todos', response_model=List[schema.ResponseSchema])
@cache(expire=60)  # Cache for 60 seconds
async def getTodos(db: Session = Depends(get_db)):
    todoData = db.query(models.Todos).all()
    return todoData

@app.post('/create_todo', status_code=status.HTTP_201_CREATED, response_model=schema.ResponseSchema)
async def CreateTodo(Todo: schema.TodoCreate, db: Session = Depends(get_db)):
    todo_data = Todo.model_dump(exclude_unset=True)
    new_todo = models.Todos(**todo_data)
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    await FastAPICache.clear(namespace="todos")  # Clear cache after creating
    return new_todo

@app.put('/update_todo/{id}', status_code=status.HTTP_201_CREATED, response_model=schema.ResponseSchema)
async def updateTodo(id: int, Todo: schema.TodoCreate, db: Session = Depends(get_db)):
    todoData = db.query(models.Todos).filter(models.Todos.id == id)
    data = todoData.first()
    if data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with id {id} not found")
    todoData.update(Todo.model_dump(), synchronize_session=False)
    db.commit()
    db.refresh(data)
    await FastAPICache.clear(namespace="todos")  # Clear cache after updating
    return data

@app.delete('/delete_todo/{id}')
async def deleteTodo(id: int, db: Session = Depends(get_db)):
    deleteTodo = db.query(models.Todos).filter(models.Todos.id == id)
    if deleteTodo.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")
    deleteTodo.delete(synchronize_session=False)
    db.commit()
    await FastAPICache.clear(namespace="todos")  # Clear cache after deleting
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.get('/todo/{id}', response_model=schema.ResponseSchema)
@cache(expire=60)  # Cache for 60 seconds
async def getOneTodo(id: int, db: Session = Depends(get_db)):
    data = db.query(models.Todos).filter(models.Todos.id == id).first()
    if data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with id {id} not found")
    return data