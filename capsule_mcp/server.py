"""Capsule CRM MCP Server

Exposes common Capsule CRM operations as Model Context Protocol (MCP) tools.

Run locally:
    uvicorn capsule_mcp.server:app --reload --port 8000
"""

import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

import httpx
from fastapi import FastAPI
from fastmcp import FastMCP
from fastmcp.server.auth import BearerAuthProvider
from fastmcp.server.auth.providers.bearer import RSAKeyPair
from pydantic import BaseModel

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

# Generate a test key pair for development
key_pair = RSAKeyPair.generate()

# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

class Person(BaseModel):
    """A person contact in Capsule CRM."""
    first_name: str
    last_name: str
    email: Optional[str] = None
    organisation: Optional[str] = None
    tags: Optional[List[str]] = None

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
mcp = FastMCP(
    name="Capsule CRM MCP",
    description=(
        "Exposes common Capsule CRM actions (contact search, creation, notes, "
        "tasks, and opportunities) as Model Context Protocol tools so that AI "
        "assistants can read and update your pipeline in a secure, auditable "
        "way."
    ),
    auth=BearerAuthProvider(public_key=key_pair.public_key),
)

if os.getenv("PYTEST_CURRENT_TEST"):
    app = mcp.http_app()
else:
    app = FastAPI()
    app.mount("/mcp", mcp.http_app())

# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool
async def list_contacts(
    page: int = 1,
    per_page: int = 50,
    archived: bool = False,
) -> Dict[str, Any]:
    """Return a paginated list of contacts."""
    params = {
        "page": page,
        "perPage": per_page,
        "archived": str(archived).lower(),
    }
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
async def create_person(person: Person) -> Dict[str, Any]:
    """Create a person contact in Capsule."""
    payload = {
        "party": {
            "type": "person",
            "firstName": person.first_name,
            "lastName": person.last_name,
            "email": person.email,
            "organisation": person.organisation,
            "tags": [{"name": tag} for tag in (person.tags or [])],
        }
    }
    return await capsule_request("POST", "parties", json=payload)

@mcp.tool
async def add_note(
    party_id: int,
    note: str,
) -> Dict[str, Any]:
    """Attach a note to an existing party."""
    payload = {"entry": {"type": "note", "content": note}}
    return await capsule_request("POST", f"parties/{party_id}/entries", json=payload)

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
    import uvicorn
    
    uvicorn.run(
        "capsule_mcp.server:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )
