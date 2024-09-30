from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TodoBase(BaseModel):
    title: str
    todo: str
    expiry_date: Optional[datetime] = None


class TodoCreate(TodoBase):
    pass

class TodoSchema(TodoBase):
    id: int
    date_created: datetime

    class Config:
        from_attributes = True

class ResponseSchema(TodoSchema):
    pass