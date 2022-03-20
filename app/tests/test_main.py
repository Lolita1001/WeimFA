from fastapi.testclient import TestClient


from app.main import app
from app.db.database import get_session
from app.tests.test_db import override_get_session

app.dependency_overrides[get_session] = override_get_session
client = TestClient(app)


def test_get_user_by_id_or_email():
    response = client.get("/api/v1/users")
    assert response.status_code == 200
    assert response.json() == []
