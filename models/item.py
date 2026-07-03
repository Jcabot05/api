from pydantic import BaseModel


class Item(BaseModel):
   item_name: str
   description: str | None = None
   price: float | None = None
   tax: float | None = None