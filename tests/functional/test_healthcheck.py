import requests


def test_healthcheck():
    """Test service readiness."""
    response = requests.get("http://localhost:8080/healthcheck")
    assert response.status_code == 200
    assert response.content == b"Health check OK"
