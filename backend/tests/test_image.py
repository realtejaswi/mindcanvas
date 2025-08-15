import pytest
from fastapi.testclient import TestClient

def test_generate_image(client: TestClient, auth_headers):
    """Test image generation."""
    response = client.post(
        "/image/generate",
        json={
            "prompt": "a beautiful sunset",
            "width": 512,
            "height": 512,
            "steps": 20
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["prompt"] == "a beautiful sunset"
    assert "meta_data" in data

def test_generate_image_unauthorized(client: TestClient):
    """Test image generation without authentication."""
    response = client.post(
        "/image/generate",
        json={
            "prompt": "test image",
            "width": 256,
            "height": 256
        }
    )
    assert response.status_code == 401

def test_get_image_history(client: TestClient, auth_headers):
    """Test getting image generation history."""
    # First generate an image
    client.post(
        "/image/generate",
        json={
            "prompt": "test image",
            "width": 256,
            "height": 256
        },
        headers=auth_headers
    )

    # Then get history
    response = client.get("/image/history", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:  # If there are results
        assert "prompt" in data[0]
        assert "meta_data" in data[0]

def test_get_image_history_pagination(client: TestClient, auth_headers):
    """Test image history pagination."""
    response = client.get(
        "/image/history?skip=0&limit=5",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 5