from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import UserList, UserPublic, UserSchema
from fast_zero.security import get_current_user, get_password_hash
from typing import Annotated

router = APIRouter(
    prefix='',
    tags=['users']
)
T_Session = Annotated[Session, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user())]


@router.get("/", response_model=UserList)
def read_users(session: T_Session, limit: int = 10,
               skip: int = 0,):
    user = session.scalars(select(User).limit(limit).offset(skip))
    return {"users": database}


@router.put("/{user_id}", response_model=UserPublic)
def update_user(user_id: int, user: UserSchema,
                session: T_Session,
                current_user: T_CurrentUser):

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


@router.delete("/{user_id}", response_model=UserPublic)
def delete_user(user_id: int, session: T_Session,
                current_user: T_CurrentUser):

    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )
    session.delete(current_user)
    session.commit()

    return {"message": "User deleted"}


@router.post("/", status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: T_Session):
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
