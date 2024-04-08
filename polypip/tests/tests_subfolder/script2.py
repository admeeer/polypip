from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    a: int
    b: int

@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI test API!"}

@app.post("/add")
async def add_numbers(item: Item):
    result = item.a + item.b
    return {"result": result}
