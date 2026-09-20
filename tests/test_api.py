import pytest
from fastapi.testclient import TestClient
from app.backend.main import app

client = TestClient(app)


def test_health_endpoint():
    """Tests the /health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]


def test_documents_endpoint():
    """Tests the /documents listing endpoint."""
    response = client.get("/documents")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_ask_empty_question():
    """Tests validation on empty question submission."""
    response = client.post("/ask", json={"question": ""})
    assert response.status_code == 400
    assert "Question cannot be empty" in response.json()["detail"]


def test_upload_invalid_filetype():
    """Tests rejecting non-PDF file uploads."""
    response = client.post(
        "/upload",
        files={"files": ("test.txt", b"Hello World", "text/plain")},
        data={"category": "IT"}
    )
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]
