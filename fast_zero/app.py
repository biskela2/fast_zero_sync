from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException

from fast_zero.schemas import UserPublic
from fast_zero.routers import users, auth

app = FastAPI()
app.include_router(users.router)
app.include_router(auth.router)

@app.get("/", status_code=HTTPStatus.OK, response_model=UserPublic)
def read_root():
    return {"message": "Hello World"}



