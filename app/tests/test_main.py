import pytest
from fastapi.testclient import TestClient

from main import app
from db.database import get_session
from tests.test_db import override_get_session

app.dependency_overrides[get_session] = override_get_session
client = TestClient(app, root_path='/app')

GLOBAL_STORAGE_FOR_TEST = {}


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


@pytest.mark.parametrize("dog_id", [-1, 0, 1])
def test_get_dog_by_id(dog_id):
    response = client.get(f"/api/v1/dogs/{dog_id}")
    assert response.status_code == 200
    assert response.json() is None


def test_get_dogs_1():
    response = client.get(f"/api/v1/dogs/")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize("dog_id", [-1, 0, 1])
def test_get_media_dog_1(dog_id):
    response = client.get(f"/api/v1/media_dog/{dog_id}")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize("login, email, first_name, last_name, password",
                         [("user1", "user1@example.com", "User1", "Userovich1", "password1"),
                          ("user2", "user2@example.com", "User2", "Userovich2", "password2")])
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
    act_token = response.headers.get('act_token', 'token_not_found')
    response = client.post(f"/api/v1/users/activate/{act_token}")
    assert response.status_code == 202


@pytest.mark.parametrize("login, password", [('wrong_login', 'wrong_password'),
                                             ('user1', 'wrong_password'),
                                             ('wrong_login', 'password1')
                                             ])
def test_login_and_authentication_bad(login, password):
    response = client.post(f"/api/v1/security/token",
                           headers={
                               "accept": "application/json",
                               "Content-Type": "application/x-www-form-urlencoded"
                           },
                           data={
                               "grant_type": "password",
                               "username": login,
                               "password": password,
                               "scope": None,
                               "client_id": None,
                               "client_secret": None
                           }
                           )
    assert response.status_code == 401
    token = response.headers.get('access_token', None)
    token_type = response.headers.get('token_type', None)
    response = client.get(f"/api/v1/security/about_me",
                          headers={
                              "accept": "application/json",
                              "Authorization": f"{token_type} {token}"
                          }
                          )
    assert response.status_code == 401


@pytest.mark.parametrize("login, password", [('user1@example.com', 'password1'),
                                             ('user2@example.com', 'password2')
                                             ])
def test_login_and_authentication_ok(login, password):
    response = client.post(f"/api/v1/security/token",
                           headers={
                               "accept": "application/json",
                               "Content-Type": "application/x-www-form-urlencoded"
                           },
                           data={
                               "grant_type": "password",
                               "username": login,
                               "password": password,
                               "scope": None,
                               "client_id": None,
                               "client_secret": None
                           }
                           )
    assert response.status_code == 200
    token = response.json().get('access_token', None)
    token_type = response.json().get('token_type', None)
    response = client.get(f"/api/v1/security/about_me",
                          headers={
                              "accept": "application/json",
                              "Authorization": f"{token_type} {token}"
                          }
                          )
    assert response.status_code == 200  # TODO не выполнится, нет этапа активации аккаунта


@pytest.mark.parametrize("login, email, first_name, last_name, password",
                         [("user1", "user3@example.com", "User3", "Userovich3", "password3"),
                          ("user4", "user1@example.com", "User4", "Userovich4", "password4"),
                          ("user5", "user5@mail", "User5", "Userovich5", "password5"),
                          ("", "user6@example.com", "User6", "Userovich6", "password6"),
                          ("user7", "", "User7", "Userovich7", "password7"),
                          ("user8", "user8@example.com", "", "Userovich8", "password8"),
                          ("user9", "user9@example.com", "User9", "Userovich9", "")])
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
                         [("user1_new", "user1@example.com", "User1", "Userovich1", "password1", "password1"),
                          ("user1", "user1@example.com", "User1", "Userovich1", "password1", "password1"),
                          ("user1 new", "user1@example.com", "User1 new", "Userovich1", "password1", "password1"),
                          ("user1", "user1@example.com", "User1", "Userovich1", "password1", "password1"),
                          ("user1", "user1@example.com", "User1", "Userovich1", "password1_new", "password1"),
                          ("user1", "user1@example.com", "User1", "Userovich1", "password1", "password1_new")])
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
                         [("user1_new", "userX@example.com", "User1", "Userovich1", "password1", "password1"),
                          ("user1_new", "user1@example.com", "User1", "Userovich1", "password1", "password1_X")])
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


@pytest.mark.parametrize("breed, description", [('Weimaraner', 'Weimaraner is the best of dog'),
                                                ('Other', 'Other dogs')])
def test_add_breed_ok(breed, description):
    response = client.post(f"/api/v1/dogs/breed/",
                           json={
                               "name": breed,
                               "description": description
                           }
                           )
    assert response.status_code == 200


@pytest.mark.parametrize("breed, description", [('', 'Weimaraner is the best of dog'),
                                                ('Other', 'Other dogs'),
                                                ('Other', '')])
def test_add_breed_bad(breed, description):
    response = client.post(f"/api/v1/dogs/breed/",
                           json={
                               "name": breed,
                               "description": description
                           }
                           )
    assert response.status_code == 409
    assert response.headers.get('custom_exc', None) == "True"


@pytest.mark.parametrize("dog_name_eng, dog_name_rus, gender, date_of_birth, date_of_death, "
                         "stamp, breed_id, owner_id, breeder_id, mother_id, father_id",
                         [
                             ("dog_name1", "имя собаки1", "Male", "01.01.2011", "", "stamp1", 1, 1, 1, 0, 0),
                             ("dog_name2", "имя собаки2", "Male", "01.01.2011", "", "stamp2", 2, 1, 0, 0, 0),
                             (
                                     "dog_name3", "имя собаки3", "Female", "01.01.2001", "01.01.2015", "stamp3", 1, 1,
                                     1, 0, 0),
                             (
                                     "dog_name4", "имя собаки4", "Female", "01.01.2001", "01.01.2015", "stamp4", 2, 1,
                                     0, 0, 0),
                         ])
def test_add_dog_ok(dog_name_eng, dog_name_rus, gender, date_of_birth, date_of_death,
                    stamp, breed_id, owner_id, breeder_id, mother_id, father_id):
    response = client.post(f"/api/v1/dogs/",
                           json={
                               "dog_name_eng": dog_name_eng,
                               "dog_name_rus": dog_name_rus,
                               "gender": gender,
                               "date_of_birth": date_of_birth,
                               "date_of_death": date_of_death,
                               "stamp": stamp,
                               "breed_id": breed_id,
                               "owner_id": owner_id,
                               "breeder_id": breeder_id,
                               "mother_id": mother_id,
                               "father_id": father_id
                           }
                           )
    assert response.status_code == 200


@pytest.mark.parametrize("dog_name_eng, dog_name_rus, gender, date_of_birth, date_of_death, "
                         "stamp, breed_id, owner_id, breeder_id, mother_id, father_id",
                         [
                             ("dog_name10", "имя собаки10", "Male", "01.01.2011", "", "stamp1", 1, 1, 1, 0, 0),
                             ("dog_name11", "имя собаки11", "Male", "01.01.2011", "", "", 1, 1, 1, 0, 0),
                             ("dog_name12", "имя собаки12", "Male", "", "", "stamp12", 1, 1, 1, 0, 0),
                             ("dog_name13", "имя собаки13", "Malee", "01.01.2011", "", "stamp13", 1, 1, 1, 0, 0),
                             ("dog_name14", "имя собаки14", "Male", "01.01.2011", "", "stamp14", 14, 1, 1, 0, 0),
                             ("dog_name15", "имя собаки15", "Male", "01.01.2011", "", "stamp15", 1, 1, 15, 0, 0)
                         ])
def test_add_dog_bad(dog_name_eng, dog_name_rus, gender, date_of_birth, date_of_death,
                     stamp, breed_id, owner_id, breeder_id, mother_id, father_id):
    response = client.post(f"/api/v1/dogs/",
                           json={
                               "dog_name_eng": dog_name_eng,
                               "dog_name_rus": dog_name_rus,
                               "gender": gender,
                               "date_of_birth": date_of_birth,
                               "date_of_death": date_of_death,
                               "stamp": stamp,
                               "breed_id": breed_id,
                               "owner_id": owner_id,
                               "breeder_id": breeder_id,
                               "mother_id": mother_id,
                               "father_id": father_id
                           }
                           )
    assert response.status_code in [401, 409, 422]
    if dog_name_eng != "dog_name13":
        assert response.headers.get('custom_exc', None) == "True"


@pytest.mark.parametrize("dog_id, img_path",
                         [(1, "tests/test_static/img_1.png"),
                          (1, "tests/test_static/img_1.png"),
                          (1, "tests/test_static/img_2.png"),
                          (2, "tests/test_static/img_1.png"),
                          (2, "tests/test_static/img_1.png"),
                          (2, "tests/test_static/img_2.png")])
def test_create_file_dog_ok(dog_id, img_path):
    files = {'in_file': open(img_path, 'rb')}
    response = client.post(f"/api/v1/media_dog/{dog_id}", files=files)
    assert response.status_code == 200


@pytest.mark.parametrize("dog_id, img_path",
                         [(30, "tests/test_static/img_1.png"),
                          (1, "tests/test_static/img_3_large.jpg"),
                          (1, "tests/test_static/img_4.ico")])
def test_create_file_dog_bad(dog_id, img_path):
    files = {'in_file': open(img_path, 'rb')}
    response = client.post(f"/api/v1/media_dog/{dog_id}", files=files)
    assert response.status_code in [401, 409, 411]
    assert response.headers.get('custom_exc', None) == "True"


@pytest.mark.parametrize("dog_id", [2, 4, 6])
def test_delete_media_dog_ok(dog_id):
    response = client.delete(f"/api/v1/media_dog/{dog_id}")
    assert response.status_code == 200


@pytest.mark.parametrize("dog_id", [10, 11])
def test_delete_media_dog_bad(dog_id):
    response = client.delete(f"/api/v1/media_dog/{dog_id}")
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
