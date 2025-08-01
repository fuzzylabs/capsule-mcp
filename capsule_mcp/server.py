"""Example Capsule CRM MCP Server.

This minimal server exposes read only Capsule CRM operations as Model Context
Protocol (MCP) tools.  It is intentionally simple so it can be used as a
reference implementation when integrating Capsule with AI assistants.

Run locally:
    uvicorn capsule_mcp.server:app --reload
"""

import os
from typing import Any, Dict, Literal

from dotenv import load_dotenv

# Type definitions
EntityType = Literal["opportunities", "parties", "kases"]

import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastmcp import FastMCP

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

# MCP API key for authenticating requests to the MCP endpoints
MCP_API_KEY = os.getenv("MCP_API_KEY")


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
        "User-Agent": "capsule-mcp/0.1.0 (+https://github.com/fuzzylabs/capsule-mcp)",
    }

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.request(method, url, headers=headers, **kwargs)

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            if exc.response.headers.get("content-type", "").startswith(
                "application/json"
            ):
                detail = exc.response.json()
            else:
                detail = exc.response.text
            raise RuntimeError(
                f"Capsule API error {exc.response.status_code}: {detail}"
            ) from None

        return response.json()


# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------

# Create the MCP server
mcp_auth = None

mcp = FastMCP(
    name="Capsule CRM MCP",
    auth=mcp_auth,
    json_response=True,
    stateless_http=True,
)


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------


async def authenticate_request(request: Request):
    """Authenticate requests to MCP endpoints using API key."""
    # Skip authentication for tests
    if os.getenv("PYTEST_CURRENT_TEST"):
        return

    # Skip authentication if no API key is configured
    if not MCP_API_KEY:
        return

    # Only authenticate /mcp/ endpoints
    if not request.url.path.startswith("/mcp"):
        return

    # Check for Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(
            status_code=401,
            detail="Missing Authorization header. Use 'Authorization: Bearer <api_key>'",
        )

    # Validate Bearer token format
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid Authorization header format. Use 'Authorization: Bearer <api_key>'",
        )

    provided_key = auth_header[7:]
    if provided_key != MCP_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------


def create_app() -> FastAPI:
    """Return a new FastAPI application with the MCP routes mounted."""
    mcp_app = mcp.http_app(path="/")

    app = FastAPI(lifespan=mcp_app.lifespan)

    # Add authentication middleware
    @app.middleware("http")
    async def auth_middleware(request: Request, call_next):
        await authenticate_request(request)
        response = await call_next(request)
        return response

    app.mount("/mcp", mcp_app)

    @app.api_route("/mcp", methods=["GET", "POST"])
    async def mcp_redirect() -> RedirectResponse:
        """Redirect ``/mcp`` to ``/mcp/`` preserving the request method."""
        return RedirectResponse(url="/mcp/", status_code=307)

    return app


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
            "conditions": [{"field": "type", "operator": "is", "value": "person"}],
            "orderBy": [{"field": "lastContactedOn", "direction": "descending"}],
        },
        "page": page,
        "perPage": per_page,
    }
    return await capsule_request("POST", "parties/filters/results", json=filter_data)


@mcp.tool
async def list_opportunities(
    page: int = 1,
    per_page: int = 50,
    since: str = None,
    embed: str = "tags,fields",
) -> Dict[str, Any]:
    """Return a paginated list of opportunities.

    Args:
        page: Page number (default: 1)
        per_page: Number of opportunities per page (default: 50, max: 100)
        since: Only return opportunities modified since this date (ISO8601 format, e.g. '2024-01-01T00:00:00Z')
        embed: Comma-separated list of data to embed (default: "tags,fields")
    """
    params = {
        "page": page,
        "perPage": per_page,
    }
    if since:
        params["since"] = since
    if embed:
        params["embed"] = embed

    return await capsule_request("GET", "opportunities", params=params)


@mcp.tool
async def list_open_opportunities(
    page: int = 1,
    per_page: int = 50,
) -> Dict[str, Any]:
    """Return open opportunities using filters API for proper filtering and sorting."""
    filter_data = {
        "filter": {
            "conditions": [
                {"field": "milestone", "operator": "is not", "value": "won"},
                {"field": "milestone", "operator": "is not", "value": "lost"},
            ],
            "orderBy": [{"field": "expectedCloseOn", "direction": "ascending"}],
        },
        "page": page,
        "perPage": per_page,
    }
    return await capsule_request(
        "POST", "opportunities/filters/results", json=filter_data
    )


# Cases/Support
@mcp.tool
async def list_cases(
    page: int = 1,
    per_page: int = 50,
    since: str = None,
    embed: str = "tags,fields,opportunity",
) -> Dict[str, Any]:
    """Return a paginated list of support cases.

    Args:
        page: Page number (default: 1)
        per_page: Number of cases per page (default: 50, max: 100)
        since: Only return cases modified since this date (ISO8601 format)
        embed: Comma-separated list of data to embed
            (default: "tags,fields,opportunity")
    """
    params = {
        "page": page,
        "perPage": per_page,
    }
    if since:
        params["since"] = since
    if embed:
        params["embed"] = embed

    return await capsule_request("GET", "kases", params=params)


@mcp.tool
async def search_cases(
    keyword: str,
    page: int = 1,
    per_page: int = 50,
) -> Dict[str, Any]:
    """Search support cases by keyword."""
    params = {"q": keyword, "page": page, "perPage": per_page}
    return await capsule_request("GET", "kases/search", params=params)


@mcp.tool
async def get_case(case_id: int, embed: str = "tags,fields,opportunity") -> Dict[str, Any]:
    """Get detailed information about a specific support case.
    
    Args:
        case_id: The ID of the support case to retrieve
        embed: Comma-separated list of data to embed
            (default: "tags,fields,opportunity")
    """
    params = {"embed": embed} if embed else {}
    return await capsule_request("GET", f"kases/{case_id}", params=params)


# Tasks
@mcp.tool
async def list_tasks(
    page: int = 1,
    per_page: int = 50,
    since: str = None,
) -> Dict[str, Any]:
    """Return a paginated list of tasks.

    Args:
        page: Page number (default: 1)
        per_page: Number of tasks per page (default: 50, max: 100)
        since: Only return tasks modified since this date (ISO8601 format)
    """
    params = {
        "page": page,
        "perPage": per_page,
    }
    if since:
        params["since"] = since

    return await capsule_request("GET", "tasks", params=params)


@mcp.tool
async def get_task(task_id: int) -> Dict[str, Any]:
    """Get detailed information about a specific task."""
    return await capsule_request("GET", f"tasks/{task_id}")


# Timeline Entries
@mcp.tool
async def list_entries(
    page: int = 1,
    per_page: int = 50,
    since: str = None,
) -> Dict[str, Any]:
    """Return timeline entries (notes, emails, calls, etc.).

    Args:
        page: Page number (default: 1)
        per_page: Number of entries per page (default: 50, max: 100)
        since: Only return entries modified since this date (ISO8601 format)
    """
    params = {
        "page": page,
        "perPage": per_page,
    }
    if since:
        params["since"] = since

    return await capsule_request("GET", "entries", params=params)


@mcp.tool
async def get_entry(entry_id: int) -> Dict[str, Any]:
    """Get detailed information about a specific timeline entry."""
    return await capsule_request("GET", f"entries/{entry_id}")


# Projects
@mcp.tool
async def list_projects(
    page: int = 1,
    per_page: int = 50,
    since: str = None,
    embed: str = "tags,fields,opportunity",
) -> Dict[str, Any]:
    """Return a paginated list of projects.

    Args:
        page: Page number (default: 1)
        per_page: Number of projects per page (default: 50, max: 100)
        since: Only return projects modified since this date (ISO8601 format)
        embed: Comma-separated list of data to embed (default: "tags,fields,opportunity")
    """
    params = {
        "page": page,
        "perPage": per_page,
    }
    if since:
        params["since"] = since
    if embed:
        params["embed"] = embed

    return await capsule_request("GET", "projects", params=params)


@mcp.tool
async def get_project(project_id: int, embed: str = "tags,fields,opportunity") -> Dict[str, Any]:
    """Get detailed information about a specific project.
    
    Args:
        project_id: The ID of the project to retrieve
        embed: Comma-separated list of data to embed (default: "tags,fields,opportunity")
    """
    params = {"embed": embed} if embed else {}
    return await capsule_request("GET", f"projects/{project_id}", params=params)


# Tags
@mcp.tool
async def list_tags(
    entity: EntityType = "opportunities",
    page: int = 1,
    per_page: int = 50,
) -> Dict[str, Any]:
    """Return a paginated list of tags for a specific entity.
    
    Args:
        entity: Entity type to get tags for. Must be one of: "opportunities", "parties", "kases" (default: "opportunities")
        page: Page number (default: 1)
        per_page: Number of tags per page (default: 50, max: 100)
    """
    params = {
        "page": page,
        "perPage": per_page,
    }
    return await capsule_request("GET", f"{entity}/tags", params=params)


@mcp.tool
async def get_tag(tag_id: int, entity: EntityType = "opportunities") -> Dict[str, Any]:
    """Get detailed information about a specific tag for an entity.
    
    Args:
        tag_id: The ID of the tag to retrieve
        entity: Entity type the tag belongs to. Must be one of: "opportunities", "parties", "kases" (default: "opportunities")
    """
    return await capsule_request("GET", f"{entity}/tags/{tag_id}")


# Users
@mcp.tool
async def list_users(
    page: int = 1,
    per_page: int = 50,
) -> Dict[str, Any]:
    """Return a paginated list of users."""
    params = {
        "page": page,
        "perPage": per_page,
    }
    return await capsule_request("GET", "users", params=params)


@mcp.tool
async def get_user(user_id: int) -> Dict[str, Any]:
    """Get detailed information about a specific user."""
    return await capsule_request("GET", f"users/{user_id}")


# Individual Contact Operations
@mcp.tool
async def get_contact(contact_id: int) -> Dict[str, Any]:
    """Get detailed information about a specific contact."""
    return await capsule_request("GET", f"parties/{contact_id}")


@mcp.tool
async def get_opportunity(opportunity_id: int, embed: str = "tags,fields") -> Dict[str, Any]:
    """Get detailed information about a specific opportunity.
    
    Args:
        opportunity_id: The ID of the opportunity to retrieve
        embed: Comma-separated list of data to embed (default: "tags,fields")
    """
    params = {"embed": embed} if embed else {}
    return await capsule_request("GET", f"opportunities/{opportunity_id}", params=params)

# Configuration Tools
@mcp.tool
async def list_pipelines() -> Dict[str, Any]:
    """Return a list of sales pipelines."""
    return await capsule_request("GET", "pipelines")


@mcp.tool
async def list_stages() -> Dict[str, Any]:
    """Return a list of pipeline stages."""
    return await capsule_request("GET", "stages")


@mcp.tool
async def list_milestones() -> Dict[str, Any]:
    """Return a list of opportunity milestones."""
    return await capsule_request("GET", "milestones")


@mcp.tool
async def list_custom_fields() -> Dict[str, Any]:
    """Return a list of custom field definitions."""
    return await capsule_request("GET", "fieldDefinitions")


# Product Catalog
@mcp.tool
async def list_products(
    page: int = 1,
    per_page: int = 50,
) -> Dict[str, Any]:
    """Return a paginated list of products."""
    params = {
        "page": page,
        "perPage": per_page,
    }
    return await capsule_request("GET", "products", params=params)


@mcp.tool
async def list_categories(
    page: int = 1,
    per_page: int = 50,
) -> Dict[str, Any]:
    """Return a paginated list of product categories."""
    params = {
        "page": page,
        "perPage": per_page,
    }
    return await capsule_request("GET", "categories", params=params)


# System Information
@mcp.tool
async def list_currencies() -> Dict[str, Any]:
    """Return a list of supported currencies."""
    return await capsule_request("GET", "currencies")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Run as MCP server via stdio
    mcp.run("stdio")
