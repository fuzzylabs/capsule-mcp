"""Tests for the Capsule CRM MCP server."""

from typing import Dict, Any
import json
import pytest
from fastapi.testclient import TestClient

from capsule_mcp.server import create_app

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    """Create a fresh FastAPI test client for each test."""
    test_app = create_app()
    with TestClient(test_app) as client:
        yield client

@pytest.fixture
def mock_capsule_response(monkeypatch):
    """Mock the Capsule API response."""
    async def mock_request(*args, **kwargs):
        return {"parties": [{"id": 1, "firstName": "Test", "lastName": "User"}]}
    
    monkeypatch.setattr("capsule_mcp.server.capsule_request", mock_request)

@pytest.fixture
def headers() -> Dict[str, str]:
    """Return standard headers for requests."""
    return {
        "Accept": "application/json, text/event-stream",
    }

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_mcp_schema(client, headers):
    """Test listing tools via the MCP endpoint."""
    response = client.post(
        "/mcp/",
        json={"jsonrpc": "2.0", "method": "tools/list", "id": 1},
        headers=headers,
    )
    assert response.status_code == 200

    tools = response.json()["result"]["tools"]
    assert len(tools) > 0

    tool_names = {tool["name"] for tool in tools}
    expected_tools = {
        "list_contacts",
        "search_contacts",
        "list_open_opportunities",
    }
    assert expected_tools.issubset(tool_names)

def test_list_contacts(client, mock_capsule_response, headers):
    """Test the list_contacts tool."""
    response = client.post(
        "/mcp/",
        json={
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "list_contacts",
                "arguments": {"page": 1, "per_page": 10},
            },
            "id": 1,
        },
        headers=headers,
    )
    assert response.status_code == 200

    payload = response.json()["result"]["content"][0]["text"]
    data = json.loads(payload)
    assert "parties" in data
    assert len(data["parties"]) > 0
    assert data["parties"][0]["firstName"] == "Test"

def test_search_contacts(client, mock_capsule_response, headers):
    """Test the search_contacts tool."""
    response = client.post(
        "/mcp/",
        json={
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "search_contacts",
                "arguments": {"keyword": "test", "page": 1, "per_page": 10},
            },
            "id": 1,
        },
        headers=headers,
    )
    assert response.status_code == 200

    payload = response.json()["result"]["content"][0]["text"]
    data = json.loads(payload)
    assert "parties" in data
    assert len(data["parties"]) > 0

def test_list_open_opportunities(client, mock_capsule_response, headers):
    """Test the list_open_opportunities tool."""
    response = client.post(
        "/mcp/",
        json={
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "list_open_opportunities",
                "arguments": {"page": 1, "per_page": 10},
            },
            "id": 1,
        },
        headers=headers,
    )
    assert response.status_code == 200

def test_invalid_tool(client, headers):
    """Invalid tool names should return an error result."""
    response = client.post(
        "/mcp/",
        json={
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": "invalid_tool", "arguments": {}},
            "id": 1,
        },
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["result"]["isError"] is True
def test_missing_required_args(client, headers):
    """Missing arguments should produce an error result."""
    response = client.post(
        "/mcp/",
        json={
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": "search_contacts", "arguments": {}},
            "id": 1,
        },
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["result"]["isError"] is True

def test_print_routes(client):
    """Ensure that the MCP endpoint is registered."""
    routes = [route.path for route in client.app.routes if hasattr(route, "path")]
    assert "/mcp" in routes

def test_debug_post_to_mcp(client, headers):
    """Verify the MCP schema can be retrieved."""
    response = client.post(
        "/mcp/",
        json={"jsonrpc": "2.0", "method": "tools/list", "id": 1},
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "result" in data and "tools" in data["result"]

def test_mcp_redirect(client, headers):
    """Requests to /mcp should redirect to /mcp/."""
    response = client.post(
        "/mcp",
        json={"jsonrpc": "2.0", "method": "tools/list", "id": 1},
        follow_redirects=True,
        headers=headers,
    )
    assert response.status_code == 200
