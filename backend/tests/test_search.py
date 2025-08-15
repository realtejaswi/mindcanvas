import pytest
from fastapi.testclient import TestClient

def test_perform_search(client: TestClient, auth_headers):
    """Test performing a web search."""
    response = client.post(
        "/search/",
        json={
            "query": "artificial intelligence",
            "max_results": 5
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "artificial intelligence"
    assert "results" in data
    assert len(data["results"]) <= 5

def test_perform_search_unauthorized(client: TestClient):
    """Test search without authentication."""
    response = client.post(
        "/search/",
        json={
            "query": "test query",
            "max_results": 5
        }
    )
    assert response.status_code == 401

def test_get_search_history(client: TestClient, auth_headers):
    """Test getting search history."""
    # First perform a search
    client.post(
        "/search/",
        json={"query": "test query", "max_results": 3},
        headers=auth_headers
    )

    # Then get history
    response = client.get("/search/history", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:  # If there are results
        assert "query" in data[0]
        assert "results" in data[0]

def test_get_search_history_pagination(client: TestClient, auth_headers):
    """Test search history pagination."""
    response = client.get(
        "/search/history?skip=0&limit=5",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 5