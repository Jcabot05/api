from pydantic import BaseModel


class FormData(BaseModel):
   item_name: str
   description: str
   price: float
   tax: float