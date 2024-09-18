from sqlalchemy import select

from fast_zero.models import User


def test_create_user(session):
    user = User(username="Matheus", email="<EMAIL>", password="<PASSWORD>")

    session.add(user)
    session.commit()

    result = session.scalar(select(User).where(User.email == "<EMAIL>"))

    assert result.username == "Matheus"
