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


def test_get_users_1():
    response = client.get(f"/api/v1/users/")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize("user_id", [-1, 0, 1])
def test_get_media_user_1(user_id):
    response = client.get(f"/api/v1/media_user/{user_id}")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize("login, email, first_name, last_name, password",
                         [("user1", "user1@mail.ru", "User1", "Userovich1", "password1"),
                          ("user2", "user2@mail.ru", "User2", "Userovich2", "password2")])
def test_add_user_ok(login, email, first_name, last_name, password):
    response = client.post(f"/api/v1/users/",
                           json={
                               "login": login,
                               "email": email,
                               "first_name": first_name,
                               "last_name": last_name,
                               "password": password
                           }
                           )
    assert response.status_code == 200


@pytest.mark.parametrize("login, email, first_name, last_name, password",
                         [("user1", "user3@mail.ru", "User3", "Userovich3", "password3"),
                          ("user4", "user1@mail.ru", "User4", "Userovich4", "password4"),
                          ("user5", "user5@mail", "User5", "Userovich5", "password5"),
                          ("", "user6@mail.ru", "User6", "Userovich6", "password6"),
                          ("user7", "", "User7", "Userovich7", "password7"),
                          ("user8", "user8@mail.ru", "", "Userovich8", "password8"),
                          ("user9", "user9@mail.ru", "User9", "Userovich9", "")])
def test_add_user_bad(login, email, first_name, last_name, password):
    response = client.post(f"/api/v1/users/",
                           json={
                               "login": login,
                               "email": email,
                               "first_name": first_name,
                               "last_name": last_name,
                               "password": password
                           }
                           )
    assert response.status_code in [404, 409, 422]


@pytest.mark.parametrize("login, email, first_name, last_name, password, old_password",
                         [("user1_new", "user1@mail.ru", "User1", "Userovich1", "password1", "password1"),
                          ("user1", "user1@mail.ru", "User1", "Userovich1", "password1", "password1"),
                          ("user1 new", "user1@mail.ru", "User1 new", "Userovich1", "password1", "password1"),
                          ("user1", "user1@mail.ru", "User1", "Userovich1", "password1", "password1"),
                          ("user1", "user1@mail.ru", "User1", "Userovich1", "password1_new", "password1"),
                          ("user1", "user1@mail.ru", "User1", "Userovich1", "password1", "password1_new")])
def test_update_user_ok(login, email, first_name, last_name, password, old_password):
    response = client.put(f"/api/v1/users/",
                          json={
                              "login": login,
                              "email": email,
                              "first_name": first_name,
                              "last_name": last_name,
                              "password": password,
                              "old_password": old_password
                          }
                          )
    assert response.status_code == 200


@pytest.mark.parametrize("login, email, first_name, last_name, password, old_password",
                         [("user1_new", "userX@mail.ru", "User1", "Userovich1", "password1", "password1"),
                          ("user1_new", "user1@mail.ru", "User1", "Userovich1", "password1", "password1_X")])
def test_update_user_bad(login, email, first_name, last_name, password, old_password):
    response = client.put(f"/api/v1/users/",
                          json={
                              "login": login,
                              "email": email,
                              "first_name": first_name,
                              "last_name": last_name,
                              "password": password,
                              "old_password": old_password
                          }
                          )
    assert response.status_code == 401
    assert response.headers.get('custom_exc', None) == "True"


@pytest.mark.parametrize("user_id, img_path",
                         [(1, "tests/test_static/img_1.png"),
                          (1, "tests/test_static/img_1.png"),
                          (1, "tests/test_static/img_2.png"),
                          (2, "tests/test_static/img_1.png"),
                          (2, "tests/test_static/img_1.png"),
                          (2, "tests/test_static/img_2.png")])
def test_create_file_ok(user_id, img_path):
    files = {'in_file': open(img_path, 'rb')}
    response = client.post(f"/api/v1/media_user/{user_id}", files=files)
    assert response.status_code == 200


@pytest.mark.parametrize("user_id, img_path",
                         [(3, "tests/test_static/img_1.png"),
                          (1, "tests/test_static/img_3_large.jpg"),
                          (1, "tests/test_static/img_4.ico")])
def test_create_file_bad(user_id, img_path):
    files = {'in_file': open(img_path, 'rb')}
    response = client.post(f"/api/v1/media_user/{user_id}", files=files)
    assert response.status_code in [401, 409, 411]
    assert response.headers.get('custom_exc', None) == "True"


@pytest.mark.parametrize("media_id", [2, 4, 6])
def test_delete_media_user_ok(media_id):
    response = client.delete(f"/api/v1/media_user/{media_id}")
    assert response.status_code == 200


@pytest.mark.parametrize("media_id", [10, 11])
def test_delete_media_user_bag(media_id):
    response = client.delete(f"/api/v1/media_user/{media_id}")
    assert response.status_code == 401
    assert response.headers.get('custom_exc', None) == "True"


@pytest.mark.parametrize("user_id", [1, 2])
def test_delete_user_by_id_ok(user_id):
    response = client.delete(f"/api/v1/users/{user_id}")
    assert response.status_code == 200


def test_get_users_2():
    response = client.get(f"/api/v1/users/")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize("user_id", [1, 2])
def test_get_media_user_2(user_id):
    response = client.get(f"/api/v1/media_user/{user_id}")
    assert response.status_code == 200
    assert response.json() == []
