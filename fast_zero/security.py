from datetime import datetime, timedelta
from http import HTTPStatus

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import DecodeError, ExpiredSignatureError, decode, encode, PyJWTError
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session
from zoneinfo import ZoneInfo

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import TokenData
from fast_zero.settings import Settings

settings = Settings()
pwd_context = PasswordHash.recommended()


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({'exp': expire, 'sub': data.get('username')})
    encoded_jwt = encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/token')


def get_current_user(
        session: Session = Depends(get_session),
        token: str = Depends(oauth2_scheme),
):
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    print(f"Token recebido: {token}")

    try:
        print("Decodificando o token...")
        payload = decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        print(f"Payload decodificado: {payload}")

        username: str = payload.get('sub')
        if not username:
            print("Username não encontrado no payload.")
            raise credentials_exception

        token_data = TokenData(username=username)
    except DecodeError:
        print("Erro ao decodificar o token.")
        raise credentials_exception
    except ExpiredSignatureError:
        print("O token expirou.")
        raise credentials_exception
    except Exception as e:
        print(f"Erro ao processar o token: {str(e)}")
        raise credentials_exception

    print(f"Buscando usuário: {username}")
    user = session.scalar(
        select(User).where(User.email == username)
    )

    if not user:
        print("Usuário não encontrado.")
        raise credentials_exception

    print("Usuário validado com sucesso.")
    return user