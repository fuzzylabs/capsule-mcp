"""Tests for the Capsule CRM MCP server."""

from typing import Dict, Any
import pytest
from fastapi.testclient import TestClient

from capsule_mcp.server import app

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)

@pytest.fixture
def mock_capsule_response(monkeypatch):
    """Mock the Capsule API response."""
    async def mock_request(*args, **kwargs):
        return {"parties": [{"id": 1, "firstName": "Test", "lastName": "User"}]}
    
    monkeypatch.setattr("capsule_mcp.server.capsule_request", mock_request)

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_mcp_schema(client):
    """Test that the MCP schema endpoint returns the correct tools."""
    response = client.post("/mcp/", json={"type": "schema"})
    assert response.status_code == 200
    
    data = response.json()
    assert "tools" in data
    assert len(data["tools"]) > 0
    
    # Check that our tools are in the schema
    tool_names = {tool["name"] for tool in data["tools"]}
    expected_tools = {
        "list_contacts",
        "search_contacts",
        "list_open_opportunities",
    }
    assert expected_tools.issubset(tool_names)

def test_list_contacts(client, mock_capsule_response):
    """Test the list_contacts tool."""
    response = client.post(
        "/mcp/",
        json={
            "type": "tool",
            "tool": "list_contacts",
            "args": {"page": 1, "per_page": 10},
        },
    )
    assert response.status_code == 200
    
    data = response.json()
    assert "parties" in data
    assert len(data["parties"]) > 0
    assert data["parties"][0]["firstName"] == "Test"

def test_search_contacts(client, mock_capsule_response):
    """Test the search_contacts tool."""
    response = client.post(
        "/mcp/",
        json={
            "type": "tool",
            "tool": "search_contacts",
            "args": {"keyword": "test", "page": 1, "per_page": 10},
        },
    )
    assert response.status_code == 200
    
    data = response.json()
    assert "parties" in data
    assert len(data["parties"]) > 0

def test_list_open_opportunities(client, mock_capsule_response):
    """Test the list_open_opportunities tool."""
    response = client.post(
        "/mcp/",
        json={
            "type": "tool",
            "tool": "list_open_opportunities",
            "args": {"page": 1, "per_page": 10},
        },
    )
    assert response.status_code == 200

def test_invalid_tool(client):
    """Test that an invalid tool name returns an error."""
    response = client.post(
        "/mcp/",
        json={
            "type": "tool",
            "tool": "invalid_tool",
            "args": {},
        },
    )
    assert response.status_code == 400

def test_invalid_request_type(client):
    """Test that an invalid request type returns an error."""
    response = client.post(
        "/mcp/",
        json={
            "type": "invalid_type",
        },
    )
    assert response.status_code == 400

def test_missing_required_args(client):
    """Test that missing required arguments returns an error."""
    response = client.post(
        "/mcp/",
        json={
            "type": "tool",
            "tool": "search_contacts",
            "args": {},
        },
    )
    assert response.status_code == 400

def test_print_routes(client):
    """Ensure that the MCP endpoint is registered."""
    routes = [route.path for route in client.app.routes if hasattr(route, "path")]
    assert "/mcp/" in routes

def test_debug_post_to_mcp(client):
    """Verify the MCP schema can be retrieved."""
    response = client.post("/mcp/", json={"type": "schema"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "tools" in data

def test_mcp_redirect(client):
    """Requests to /mcp should redirect to /mcp/."""
    response = client.post("/mcp", json={"type": "schema"}, follow_redirects=True)
    assert response.status_code == 200
