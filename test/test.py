from fastapi.testclient import TestClient

from main import server

client = TestClient(server)


def test_read_main():
    response = client.get("/accounts/me")
    print(response.json())
    assert response.status_code == 401
