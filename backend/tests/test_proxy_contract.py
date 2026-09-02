from fastapi.testclient import TestClient

from app import main as main_module
from app.main import app

client = TestClient(app, base_url="https://portal.example")


def test_public_health_response_is_minimal():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_trailing_slash_redirect_keeps_public_api_prefix_and_https():
    response = client.get("/api/health/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "https://portal.example/api/health"


def test_docs_load_openapi_from_public_api_prefix():
    response = client.get("/api/docs")

    assert response.status_code == 200
    assert "url: '/api/openapi.json'" in response.text


def test_openapi_schema_declares_public_api_server():
    response = client.get("/api/openapi.json")

    assert response.status_code == 200
    assert response.json()["servers"] == [{"url": "/api"}]


def test_public_overview_is_read_only(monkeypatch):
    class ReadOnlySession:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def scalar(self, statement):
            return 7

        def add(self, value):
            raise AssertionError("GET must not write to the database")

        def commit(self):
            raise AssertionError("GET must not commit a database transaction")

    monkeypatch.setattr(main_module, "Session", lambda engine: ReadOnlySession())

    response = client.get("/api/overview")

    assert response.status_code == 200
    assert response.json() == {"database": "연결됨", "visits": 7}
