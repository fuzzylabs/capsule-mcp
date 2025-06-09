# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Capsule CRM MCP (Model Context Protocol) server that exposes Capsule CRM API endpoints as AI tools. It's built using FastMCP framework with FastAPI backend and provides read-only access to Capsule CRM data.

The server can run in two modes:
- **stdio mode**: For direct integration with Claude Desktop and other MCP clients
- **HTTP mode**: For testing and development via REST endpoints

## Development Commands

### Testing
```bash
uv run pytest                       # Run all tests
uv run pytest tests/test_server.py::test_list_contacts  # Run specific test
uv run pytest -v                    # Verbose output
```

### Development Server (HTTP mode)
```bash
uv run uvicorn capsule_mcp.server:app --reload  # Start dev server at http://localhost:8000/mcp/
```

### MCP Server (stdio mode)
```bash
uv run python capsule_mcp/server.py # Run as MCP server via stdio
```

### Installation
```bash
uv sync                             # Install dependencies and create virtual environment
uv sync --dev                       # Install with dev dependencies (black, isort, pytest, ruff)
```

## Architecture

### Core Components

- **`capsule_mcp/server.py`**: Main server implementation containing all MCP tools and FastAPI application
- **`capsule_request()`**: Centralized HTTP client for Capsule CRM API calls with auth and error handling
- **FastMCP framework**: Handles MCP protocol implementation and tool registration
- **Tool functions**: Each decorated with `@mcp.tool` to expose Capsule CRM endpoints

### Key Patterns

1. **Tool Structure**: All tools follow the pattern of accepting pagination parameters (`page`, `per_page`) and optional filtering (`since` for date filtering)

2. **API Client**: The `capsule_request()` function handles:
   - Bearer token authentication via `CAPSULE_API_TOKEN` env var
   - Request/response processing and error handling
   - Test mode fallback (uses "test-token" when `PYTEST_CURRENT_TEST` is set)

3. **Dual Mode Operation**: 
   - **stdio**: `mcp.run("stdio")` for MCP client integration
   - **HTTP**: FastAPI app mounted at `/mcp/` for development/testing

### Tool Categories

- **Contacts**: `list_contacts`, `search_contacts`, `list_recent_contacts`, `get_contact`
- **Sales**: `list_opportunities`, `list_open_opportunities`, `get_opportunity`
- **Support**: `list_cases`, `search_cases`, `get_case`
- **Tasks**: `list_tasks`, `get_task`
- **Timeline**: `list_entries`, `get_entry`
- **Projects**: `list_projects`, `get_project`
- **Configuration**: `list_pipelines`, `list_stages`, `list_milestones`, `list_custom_fields`
- **Products**: `list_products`, `list_categories`
- **Organization**: `list_tags`, `get_tag`, `list_users`, `get_user`
- **System**: `list_currencies`

## Environment Configuration

- **`CAPSULE_API_TOKEN`**: Required for production use (get from Capsule → My Preferences → API Authentication)
- **`CAPSULE_BASE_URL`**: Defaults to `https://api.capsulecrm.com/api/v2`
- **Test mode**: Automatically detected via `PYTEST_CURRENT_TEST` environment variable

## Testing Approach

Tests use FastAPI TestClient with mocked Capsule API responses. Key test patterns:
- **Schema validation**: Verify all tools are properly registered
- **Tool execution**: Test individual tool calls with mocked responses  
- **Error handling**: Test invalid tools and missing required arguments
- **HTTP routing**: Verify MCP endpoint routing and redirects