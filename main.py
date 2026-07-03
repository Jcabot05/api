from fastapi import FastAPI

app = FastAPI()

fake_items_db = [
   {"item_name": "Foo"},
   {"item_name": "Bar"},
   {"item_name": "Baz"},
   {"item_name": "Qux"},
   {"item_name": "Quux"},
   {"item_name": "Corge"},
   {"item_name": "Grault"},
   {"item_name": "Garply"},
   {"item_name": "Waldo"},
   {"item_name": "Fred"},
   {"item_name": "Plugh"},
   {"item_name": "Xyzzy"},
   {"item_name": "Thud"},
]


@app.get("/")
def read_root():
   return {"message": "Hello World"}


@app.get("/items/{item_id}")
def read_item(item_id: int):
   return {"item_id": item_id}


@app.get("/items/")
def read_items(skip: int = 0, limit: int = 10, q: str | None = None):
   results = fake_items_db[skip : skip + limit]
   if q:
      results.append({"item_name": q})
   return results