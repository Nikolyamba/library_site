from fastapi.testclient import TestClient

from ..my_app import app

client = TestClient(app)

def test_healthcheck():
    response = client.get("/healthcheck")
    assert response.status_code == 200
    assert response.json() == {"success": True}