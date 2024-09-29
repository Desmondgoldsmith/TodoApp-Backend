from pydantic import BaseModel
from datetime import datetime

class TodoSchema(BaseModel):
    id: int
    title: str
    todo: str
    date_created: datetime
    expiry_date: datetime