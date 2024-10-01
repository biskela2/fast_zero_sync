from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import UserList, UserPublic, UserSchema, Token
from fast_zero.security import get_password_hash, verify_password,create_access_token, get_current_user

app = FastAPI()

@app.get("/", status_code=HTTPStatus.OK, response_model=UserPublic)
def read_root():
    return {"message": "Hello World"}

@app.post("/users/", status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session=Depends(get_session)):
    db_user = session.scalar(
        select(User).where((User.username == user.username) |
                           (User.email == user.email)))

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Username already taken",
            )
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Email already taken",
            )

    new_user = User(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password)
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user

@app.get("/users/", response_model=UserList)
def read_users(session: Session = Depends(get_session), limit: int = 10,
               skip: int = 0, current_user=Depends(get_current_user)):
    user = session.scalars(select(User).limit(limit).offset(skip))
    return {"users": database}


@app.put("/users/{user_id}", response_model=UserPublic)
def update_user(user_id: int, user: UserSchema,
                session: Session = Depends(get_session),
                current_user=Depends(get_current_user)):

    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )

    current_user.email = user.email
    current_user.username = user.username
    current_user.password = get_password_hash(user.password)

    session.commit()
    session.refresh(current_user)

    return current_user


@app.delete("/users/{user_id}", response_model=UserPublic)
def delete_user(user_id: int, session: Session = Depends(get_session),
                current_user=Depends(get_current_user)):

    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )
    session.delete(current_user)
    session.commit()

    return {"message": "User deleted"}

@app.post('/token')
def login_for_acess_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        session: Session = Depends(get_session)
):
    user = session.scalar(
        select(User).where(User.email == form_data.username)
    )
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=400, detail='Incorrect username or password'
        )
    access_token = create_access_token(data={'sub': user.email})

    return {"access_token": access_token, "token_type": "bearer"}

