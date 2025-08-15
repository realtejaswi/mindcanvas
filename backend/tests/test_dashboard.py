import pytest
from fastapi.testclient import TestClient

def test_get_dashboard_searches(client: TestClient, auth_headers):
    """Test getting dashboard searches."""
    response = client.get("/dashboard/search", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_dashboard_images(client: TestClient, auth_headers):
    """Test getting dashboard images."""
    response = client.get("/dashboard/images", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_export_csv(client: TestClient, auth_headers):
    """Test CSV export."""
    response = client.get("/dashboard/export/csv", headers=auth_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"

def test_export_pdf(client: TestClient, auth_headers):
    """Test PDF export."""
    response = client.get("/dashboard/export/pdf", headers=auth_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"

def test_delete_search_unauthorized(client: TestClient):
    """Test deleting search without authentication."""
    response = client.delete("/dashboard/search/1")
    assert response.status_code == 401

def test_delete_image_unauthorized(client: TestClient):
    """Test deleting image without authentication."""
    response = client.delete("/dashboard/image/1")
    assert response.status_code == 401