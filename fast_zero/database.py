from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from fast_zero.setting import settings

engine = create_engine(settings.DATABASE_URL)


def get_session():  # pragma: no cover
    with Session(engine) as session:
        return session
