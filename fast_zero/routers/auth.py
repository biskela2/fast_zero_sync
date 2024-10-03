from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import Token
from fast_zero.security import verify_password, create_access_token, get_current_user

router = APIRouter(prefix='/auth', tags=['auth'])
T_Session = Annotated[Session, Depends(get_session)]
T_OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]

@router.post('/token', response_model=Token)
def login_for_acess_token(
        form_data: T_OAuth2Form,
        session: T_Session,
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