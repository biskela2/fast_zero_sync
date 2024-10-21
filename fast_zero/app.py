from http import HTTPStatus

from fastapi import FastAPI

from fast_zero.routers import auth, users, todo
from fast_zero.schemas import UserPublic

app = FastAPI()
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(todo.router)

@app.get("/", status_code=HTTPStatus.OK, response_model=UserPublic)
def read_root():
    return {"message": "Hello World"}
