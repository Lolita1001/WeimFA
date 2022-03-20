import pytest
from fastapi.testclient import TestClient

from main import app
from db.database import get_session
from tests.test_db import override_get_session

app.dependency_overrides[get_session] = override_get_session
client = TestClient(app, root_path='/app')


@pytest.mark.parametrize("user_id", [-1, 0, 1, 'user', ' ', '123'])
def test_get_user_by_id_or_email(user_id):
    response = client.get(f"/api/v1/users/{user_id}")
    assert response.status_code == 200
    assert response.json() is None


def test_get_users():
    response = client.get(f"/api/v1/users/")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize("user_id", [-1, 0, 1])
def test_get_media_user(user_id):
    response = client.get(f"/api/v1/media_user/{user_id}")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize("login, email, full_name, password",
                         [("user1", "user1@mail.ru", "User1 U", "password1"),
                          ("user2", "user2@mail.ru", "User2 U", "password2")])
def test_add_user1(login, email, full_name, password):
    response = client.post(f"/api/v1/users/",
                           json={
                               "login": login,
                               "email": email,
                               "full_name": full_name,
                               "password": password
                           }
                           )
    assert response.status_code == 200
    # assert response.json() == []


@pytest.mark.parametrize("login, email, full_name, password",
                         [("user1", "user3@mail.ru", "User3 U", "password3"),
                          ("user4", "user1@mail.ru", "User4 U", "password4"),
                          # ("user5", "user5@mail", "User5 U", "password5"),  # TODO добавить валидацию почты
                          ("", "user6@mail.ru", "User6 U", "password6"),
                          ("user7", "", "User7 U", "password7"),
                          ("user8", "user8@mail.ru", "", "password8"),
                          ("user9", "user9@mail.ru", "User9 U", "")])
def test_add_user2(login, email, full_name, password):
    response = client.post(f"/api/v1/users/",
                           json={
                               "login": login,
                               "email": email,
                               "full_name": full_name,
                               "password": password
                           }
                           )
    assert response.status_code in [404, 409]
    # assert response.json() == []
