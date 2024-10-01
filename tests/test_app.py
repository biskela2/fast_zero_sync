from http import HTTPStatus

from fast_zero.schemas import UserPublic


def test_read_root_deve_retornar_ok_e_ola_mundo(client):
    response = client.get("/")  # Act (ação)

    assert response.status_code == HTTPStatus.OK  # Assert
    assert response.json() == {"message": "Hello World"}


def test_creat_user(client):
    response = client.post(  # UserSchema
        "/users/",
        json={
            "username": "testusername",
            "password": "password",
            "email": "test@test.com",
        },
    )

    # Voltou o status code correto?
    assert response.status_code == HTTPStatus.CREATED
    # Validar UserPublic
    assert response.json() == {
        "username": "testusername",
        "email": "test@test.com",
        "id": 1,
    }


def test_read_users(client):
    response = client.get("/users/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"users": []}


def test_read_users_with_user(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get("/users/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"users": [user_schema]}


def test_update_user(client, user, token):
    response = client.put(
        f'/users/{user.id}',
        headers={'authorization' : f'Bearer {token}'},
        json={"username": "testusername2", "email": "test@test.com", "id": user.id},
    )
    assert response.json == {
        "username": "testusername2",
        "email": "test@test.com",
        "id": user.id,
    }


def test_delete_user(client, user, token):
    response = client.delete(f"/users/{user.id}", headers={'authorization' : f'Bearer {token}'})

    assert response.json() == {
        "username": "testusername2",
        "email": "test@test.com",
        "id": user.id,
    }

def test_get_token(client, user):
    response = client.post("/token/", data={"username": user.email, "password": user.clean_password})

    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert token['token_type'] == "Bearer"
    assert 'access_token' in token
