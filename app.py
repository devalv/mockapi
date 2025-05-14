from typing import Union

from fastapi import FastAPI

mock_app = FastAPI()


@mock_app.get("/")
def read_root():
    return {"Hello": "World"}


@mock_app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
