from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_healthz():
    """Test health endpoint returns 200"""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_greet_with_name():
    """Test greeting with name parameter"""
    response = client.get("/greet?name=World")
    assert response.status_code == 200
    data = response.json()
    assert "World" in data["message"]


def test_greet_without_name():
    """Test greeting without name"""
    response = client.get("/greet")
    assert response.status_code == 200
    data = response.json()
    assert "anonymous user" in data["message"]


def test_metrics():
    """Test metrics endpoint returns Prometheus format"""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text
    assert "http_request_duration_seconds" in response.text


def test_welcome_prefix_default():
    """Test that WELCOME_PREFIX has a value (could be default or from env)"""
    import app
    assert app.WELCOME_PREFIX is not None
    assert len(app.WELCOME_PREFIX) > 0
