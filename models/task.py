from pydantic import BaseModel


class Task(BaseModel):
   id: int | None = None
   title: str
   description: str | None = None
   created_at: str | None = None