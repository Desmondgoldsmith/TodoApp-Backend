from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from .database import Base

class Todos():
    __tablename__ = 'todos'
    
    id =  Column(Integer, primary_key = True , nullable = False)
    title = Column(String, nullable = False)
    todo = Column(String, nullable = False)
    date_created = Column(TIMESTAMP(timezone = True), nullable = True , server_default =  text('now()'))
    expiry_date = Column(String,nullable = False)