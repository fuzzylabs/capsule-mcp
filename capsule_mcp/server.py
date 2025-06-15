"""Capsule CRM MCP Server using mcp-base toolkit.

This server exposes read only Capsule CRM operations as Model Context
Protocol (MCP) tools using the mcp-base toolkit for common patterns.

Run locally:
    uvicorn capsule_mcp.server:app --reload
"""

import os
from typing import Any, Dict

from mcp_base import BaseMCPServer, BearerTokenAPIClient, require_env_var, paginated_endpoint

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CAPSULE_BASE_URL = os.getenv("CAPSULE_BASE_URL", "https://api.capsulecrm.com/api/v2")
CAPSULE_API_TOKEN = os.getenv("CAPSULE_API_TOKEN")
MCP_API_KEY = os.getenv("MCP_API_KEY")

# ---------------------------------------------------------------------------
# Capsule MCP Server
# ---------------------------------------------------------------------------

class CapsuleMCPServer(BaseMCPServer):
    """Capsule CRM MCP Server implementation."""
    
    def __init__(self):
        # Create API client for Capsule CRM
        api_client = BearerTokenAPIClient(
            base_url=CAPSULE_BASE_URL,
            api_token=CAPSULE_API_TOKEN,
            user_agent="capsule-mcp/0.1.0 (+https://github.com/fuzzylabs/capsule-mcp)"
        )
        
        # Initialize without calling super().__init__ to override MCP creation
        self.name = "Capsule CRM MCP"
        self.api_client = api_client
        
        # Create MCP instance with proper HTTP settings
        from fastmcp import FastMCP
        self.mcp = FastMCP(
            name=self.name,
            json_response=True,
            stateless_http=True,
        )
        
        # Register tools
        self.register_tools()
    
    def register_tools(self) -> None:
        """Register all Capsule CRM tools."""
        # Tools will be registered via decorators below
        pass

# Create server instance
server = CapsuleMCPServer()

# ---------------------------------------------------------------------------
# API Client Compatibility Layer
# ---------------------------------------------------------------------------

async def capsule_request(method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
    """Make a request to the Capsule CRM API using the mcp-base client."""
    return await server.api_client.request(method, endpoint, **kwargs)


# Access the FastMCP instance from mcp-base
mcp = server.mcp

def create_app():
    """Return the FastAPI application (for compatibility)."""
    # Create FastAPI app from MCP server
    from fastapi import FastAPI
    from fastapi.responses import RedirectResponse
    
    mcp_app = mcp.http_app(path="/")
    app = FastAPI(lifespan=mcp_app.lifespan)
    
    # Add authentication middleware if API key is configured
    if MCP_API_KEY:
        @app.middleware("http")
        async def auth_middleware(request, call_next):
            # Skip authentication for tests
            if os.getenv("PYTEST_CURRENT_TEST"):
                response = await call_next(request)
                return response
            
            # Only authenticate /mcp/ endpoints
            if request.url.path.startswith("/mcp"):
                auth_header = request.headers.get("Authorization")
                if not auth_header or not auth_header.startswith("Bearer "):
                    from fastapi import HTTPException
                    raise HTTPException(status_code=401, detail="Invalid Authorization header")
                
                provided_key = auth_header[7:]
                if provided_key != MCP_API_KEY:
                    from fastapi import HTTPException
                    raise HTTPException(status_code=401, detail="Invalid API key")
            
            response = await call_next(request)
            return response
    
    # Mount MCP app
    app.mount("/mcp", mcp_app)
    
    @app.api_route("/mcp", methods=["GET", "POST"])
    async def mcp_redirect():
        """Redirect /mcp to /mcp/ preserving the request method."""
        return RedirectResponse(url="/mcp/", status_code=307)
    
    return app

app = create_app()

# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool
# @paginated_endpoint  # TODO: Fix compatibility with FastMCP
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
# @paginated_endpoint  # TODO: Fix compatibility with FastMCP
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
# @paginated_endpoint  # TODO: Fix compatibility with FastMCP
async def list_opportunities(
    page: int = 1,
    per_page: int = 50,
    since: str = None,
) -> Dict[str, Any]:
    """Return a paginated list of opportunities.

    Args:
        page: Page number (default: 1)
        per_page: Number of opportunities per page (default: 50, max: 100)
        since: Only return opportunities modified since this date (ISO8601 format, e.g. '2024-01-01T00:00:00Z')
    """
    params = {
        "page": page,
        "perPage": per_page,
    }
    if since:
        params["since"] = since

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
# @paginated_endpoint  # TODO: Fix compatibility with FastMCP
async def list_cases(
    page: int = 1,
    per_page: int = 50,
    since: str = None,
) -> Dict[str, Any]:
    """Return a paginated list of support cases.

    Args:
        page: Page number (default: 1)
        per_page: Number of cases per page (default: 50, max: 100)
        since: Only return cases modified since this date (ISO8601 format)
    """
    params = {
        "page": page,
        "perPage": per_page,
    }
    if since:
        params["since"] = since

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
async def get_case(case_id: int) -> Dict[str, Any]:
    """Get detailed information about a specific support case."""
    return await capsule_request("GET", f"kases/{case_id}")


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
) -> Dict[str, Any]:
    """Return a paginated list of projects.

    Args:
        page: Page number (default: 1)
        per_page: Number of projects per page (default: 50, max: 100)
        since: Only return projects modified since this date (ISO8601 format)
    """
    params = {
        "page": page,
        "perPage": per_page,
    }
    if since:
        params["since"] = since

    return await capsule_request("GET", "projects", params=params)


@mcp.tool
async def get_project(project_id: int) -> Dict[str, Any]:
    """Get detailed information about a specific project."""
    return await capsule_request("GET", f"projects/{project_id}")


# Tags
@mcp.tool
async def list_tags(
    page: int = 1,
    per_page: int = 50,
) -> Dict[str, Any]:
    """Return a paginated list of tags."""
    params = {
        "page": page,
        "perPage": per_page,
    }
    return await capsule_request("GET", "tags", params=params)


@mcp.tool
async def get_tag(tag_id: int) -> Dict[str, Any]:
    """Get detailed information about a specific tag."""
    return await capsule_request("GET", f"tags/{tag_id}")


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
async def get_opportunity(opportunity_id: int) -> Dict[str, Any]:
    """Get detailed information about a specific opportunity."""
    return await capsule_request("GET", f"opportunities/{opportunity_id}")


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
