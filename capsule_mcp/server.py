"""Example Capsule CRM MCP Server.

This minimal server exposes read only Capsule CRM operations as Model Context
Protocol (MCP) tools.  It is intentionally simple so it can be used as a
reference implementation when integrating Capsule with AI assistants.

Run locally:
    uvicorn capsule_mcp.server:app --reload
"""

import os
from typing import Any, Dict

from dotenv import load_dotenv

import httpx
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastmcp import FastMCP
# Auth imports removed since auth is disabled

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

# Load variables from a .env file if present before reading any env vars
load_dotenv()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CAPSULE_BASE_URL = os.getenv("CAPSULE_BASE_URL", "https://api.capsulecrm.com/api/v2")

# Capsule API token. For tests the ``PYTEST_CURRENT_TEST`` environment variable
# is set while requests are executed, so we lazily default to ``"test-token"``
# inside ``capsule_request`` rather than during import.
CAPSULE_API_TOKEN = os.getenv("CAPSULE_API_TOKEN")

# Auth key pair generation removed since auth is disabled

# ---------------------------------------------------------------------------
# API Client
# ---------------------------------------------------------------------------

async def capsule_request(method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
    """Make a request to the Capsule CRM API."""
    url = f"{CAPSULE_BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"

    token = CAPSULE_API_TOKEN
    if not token and os.getenv("PYTEST_CURRENT_TEST"):
        token = "test-token"
    if not token:
        raise RuntimeError(
            "CAPSULE_API_TOKEN env var is required – create one in Capsule → "
            "My Preferences → API Authentication and restart the server."
        )

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "capsule-mcp-server/0.1.0 (+https://github.com/fuzzylabs/capsule-crm-mcp-server)",
    }

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.request(method, url, headers=headers, **kwargs)
        
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            if exc.response.headers.get("content-type", "").startswith("application/json"):
                detail = exc.response.json()
            else:
                detail = exc.response.text
            raise RuntimeError(f"Capsule API error {exc.response.status_code}: {detail}") from None
            
        return response.json()

# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------

# Create the MCP server
mcp_auth = None  # Disable auth for local development

mcp = FastMCP(
    name="Capsule CRM MCP",
    description=(
        "Read only Capsule CRM tools for listing contacts and opportunities."
        "Useful as a lightweight example of the Model Context Protocol."
    ),
    auth=mcp_auth,
    json_response=True,
    stateless_http=True,
)


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

# Create the MCP app with its internal endpoint at ``/`` so that when it's
# mounted at ``/mcp`` the final URL becomes ``/mcp`` instead of ``/mcp/mcp``.
def create_app() -> FastAPI:
    """Return a new FastAPI application with the MCP routes mounted."""
    mcp_app = mcp.http_app(path="/")

    app = FastAPI(lifespan=mcp_app.lifespan)
    app.mount("/mcp", mcp_app)

    @app.api_route("/mcp", methods=["GET", "POST"])
    async def mcp_redirect() -> RedirectResponse:
        """Redirect ``/mcp`` to ``/mcp/`` preserving the request method."""
        return RedirectResponse(url="/mcp/", status_code=307)

    return app


# Create a default application instance for production use
app = create_app()

# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool
async def list_contacts(
    page: int = 1,
    per_page: int = 50,
    archived: bool = False,
    since: str = None,
) -> Dict[str, Any]:
    """Return a paginated list of contacts.
    
    Args:
        page: Page number (default: 1)
        per_page: Number of contacts per page (default: 50, max: 100)
        archived: Include archived contacts (default: false)
        since: Only return contacts modified since this date (ISO8601 format, e.g. '2024-01-01T00:00:00Z')
    """
    params = {
        "page": page,
        "perPage": per_page,
        "archived": str(archived).lower(),
    }
    if since:
        params["since"] = since
    
    return await capsule_request("GET", "parties", params=params)

@mcp.tool
async def search_contacts(
    keyword: str,
    page: int = 1,
    per_page: int = 50,
) -> Dict[str, Any]:
    """Fuzzy search contacts by name, email, or organisation."""
    params = {"q": keyword, "page": page, "perPage": per_page}
    return await capsule_request("GET", "parties/search", params=params)

@mcp.tool
async def list_recent_contacts(
    page: int = 1,
    per_page: int = 50,
) -> Dict[str, Any]:
    """Return contacts sorted by most recently contacted/updated."""
    filter_data = {
        "filter": {
            "conditions": [
                {
                    "field": "type",
                    "operator": "is",
                    "value": "person"
                }
            ],
            "orderBy": [
                {
                    "field": "lastContactedOn",
                    "direction": "descending"
                }
            ]
        },
        "page": page,
        "perPage": per_page
    }
    return await capsule_request("POST", "parties/filters/results", json=filter_data)


@mcp.tool
async def list_open_opportunities(
    page: int = 1,
    per_page: int = 50,
) -> Dict[str, Any]:
    """Return open opportunities ordered by expected close date."""
    params = {
        "page": page,
        "perPage": per_page,
        "status": "open",
        "sort": "expectedCloseDate",
    }
    return await capsule_request("GET", "opportunities", params=params)

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Run as MCP server via stdio
    mcp.run("stdio")
