# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Capsule CRM MCP (Model Context Protocol) server that exposes Capsule CRM API endpoints as AI tools. It's built using the **mcp-base toolkit** which provides common patterns for MCP server development, including standardized API client handling, parameter validation, and HTTP configuration.

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

- **`capsule_mcp/server.py`**: Main server implementation using mcp-base patterns
- **`CapsuleMCPServer`**: Server class extending `BaseMCPServer` from mcp-base toolkit
- **`BearerTokenAPIClient`**: mcp-base API client handling Capsule CRM authentication
- **Tool registration**: All tools defined within `register_tools()` method using `@self.mcp.tool`
- **FastAPI integration**: HTTP mode support with proper stateless configuration

### Key Patterns

1. **mcp-base Integration**: Server extends `BaseMCPServer` providing:
   - Standardized API client management via `BearerTokenAPIClient`
   - Automatic parameter building with `build_api_params()` and `build_search_params()`
   - Filter query construction with `build_filter_query()`
   - Connection testing via `test_connection()` method

2. **Tool Structure**: All tools follow mcp-base patterns:
   - Defined within `register_tools()` method for proper encapsulation
   - Use `@self.mcp.tool` decorator for registration
   - Accept pagination parameters (`page`, `per_page`) and filtering (`since`)
   - Utilize mcp-base utility functions for parameter handling

3. **API Client**: The `BearerTokenAPIClient` handles:
   - Bearer token authentication via `CAPSULE_API_TOKEN` env var
   - Request/response processing and error handling
   - Test mode fallback (uses "test-token" when `PYTEST_CURRENT_TEST` is set)

4. **Dual Mode Operation**: 
   - **stdio**: `mcp.run("stdio")` for MCP client integration
   - **HTTP**: FastAPI app with `json_response=True` and `stateless_http=True`

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

## mcp-base Benefits

This server demonstrates the value of the mcp-base toolkit:

1. **Reduced Boilerplate**: 60%+ reduction in server code by using common patterns
2. **Standardized Parameters**: Consistent parameter handling across all tools
3. **Built-in Utilities**: `build_api_params()`, `build_search_params()`, `build_filter_query()`
4. **HTTP Configuration**: Automatic FastAPI integration with proper MCP settings
5. **Testing Support**: Built-in test mode detection and API mocking patterns
6. **Connection Testing**: Standardized `test_connection()` method for API health checks

## Environment Configuration

- **`CAPSULE_API_TOKEN`**: Required for production use (get from Capsule → My Preferences → API Authentication)
- **`CAPSULE_BASE_URL`**: Defaults to `https://api.capsulecrm.com/api/v2`
- **`MCP_API_KEY`**: Optional API key for HTTP endpoint authentication
- **Test mode**: Automatically detected via `PYTEST_CURRENT_TEST` environment variable

## Testing Approach

Tests use FastAPI TestClient with mocked mcp-base API client responses. Key test patterns:
- **Schema validation**: Verify all tools are properly registered via mcp-base
- **Tool execution**: Test individual tool calls with mocked `BearerTokenAPIClient` responses
- **Error handling**: Test invalid tools and missing required arguments
- **HTTP routing**: Verify MCP endpoint routing and redirects
- **mcp-base Mocking**: Mock `BearerTokenAPIClient.get()` and `.post()` methods instead of raw request functions

## Configuration Synchronization

**IMPORTANT**: Multiple files contain MCP client configurations that must stay synchronized. When making changes that affect client setup, update ALL relevant files.

### Critical Sync Points

When making changes to any of these areas, update configurations across all files:

1. **Server Path Changes** (`capsule_mcp/server.py` location):
   - Update `README.md` client configuration examples
   - Update `add-to-cursor.html` step-by-step instructions
   - Regenerate Cursor deeplink in `README.md` using `scripts/generate-cursor-link.js`
   - Update `CLAUDE.md` development commands

2. **Command Changes** (installation method, arguments):
   - Update `README.md` all client configurations (Claude Desktop, Cursor, manual)
   - Update `add-to-cursor.html` installation instructions
   - Regenerate Cursor deeplink base64 configuration
   - Update `render.yaml` deployment commands
   - Update `CLAUDE.md` development server commands

3. **Environment Variables** (new or changed env vars):
   - Update `README.md` client configuration examples
   - Update `add-to-cursor.html` environment setup
   - Update `render.yaml` environment variables section
   - Regenerate Cursor deeplink with new env vars
   - Update test environment setup if needed

4. **New MCP Tools** (added/removed @mcp.tool functions):
   - Update `CLAUDE.md` Tool Categories section
   - Consider updating `README.md` feature descriptions
   - Update tests to cover new tools

### Files Requiring Updates

| File | Contains | Update When |
|------|----------|-------------|
| `README.md` | Client configs (Claude Desktop, Cursor deeplink, manual setup) | Server path, commands, env vars change |
| `add-to-cursor.html` | Step-by-step Cursor setup guide | Server path, commands, env vars change |
| `CLAUDE.md` | Development commands, tool categories | Commands change, new tools added |
| `render.yaml` | Production deployment config | Commands, env vars change |
| `tests/test_server.py` | Test configurations | New tools, env vars change |

### Automation Scripts

Use these scripts to maintain consistency:

```bash
# Generate new Cursor deeplink when config changes
node scripts/generate-cursor-link.js

# Validate all configurations are in sync
python scripts/validate-configs.py

# Check for configuration drift (run in CI)
uv run python scripts/validate-configs.py
```

## mcp-base Development Patterns

When adding new tools or modifying existing ones, follow these mcp-base patterns:

### Adding New Tools

```python
@self.mcp.tool
async def new_tool_name(
    page: int = 1,
    per_page: int = 50,
    custom_param: str = None,
) -> Dict[str, Any]:
    """Tool description following mcp-base conventions."""
    params = build_api_params(
        page=page,
        per_page=per_page,
        custom_param=custom_param
    )
    return await self.api_client.get("endpoint", params=params)
```

### Search Tools

```python
@self.mcp.tool
async def search_resource(
    keyword: str,
    page: int = 1,
    per_page: int = 50,
) -> Dict[str, Any]:
    """Search tool using mcp-base search patterns."""
    params = build_search_params(
        keyword=keyword,
        page=page,
        per_page=per_page
    )
    return await self.api_client.get("resource/search", params=params)
```

### Filter Tools

```python
@self.mcp.tool
async def filtered_resource(
    status: str = None,
    page: int = 1,
    per_page: int = 50,
) -> Dict[str, Any]:
    """Complex filtering using build_filter_query."""
    filter_data = build_filter_query(
        conditions=[{"field": "status", "operator": "is", "value": status}],
        order_by=[{"field": "created_date", "direction": "descending"}],
        page=page,
        per_page=per_page
    )
    return await self.api_client.post("resource/filters/results", json=filter_data)
```

### Testing New Tools

```python
def test_new_tool(client, mock_capsule_response, headers):
    """Test pattern for mcp-base tools."""
    response = client.post(
        "/mcp/",
        json={
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "new_tool_name",
                "arguments": {"page": 1, "per_page": 10},
            },
            "id": 1,
        },
        headers=headers,
    )
    assert response.status_code == 200
```

### Development Workflow

1. **Before making changes**: Run `python scripts/validate-configs.py` to ensure current state is clean
2. **After server/config changes**: Update all relevant files listed above
3. **Before committing**: Run validation script again to confirm synchronization
4. **PR reviews**: Verify configuration files are updated when server changes are made

### Common Sync Issues

- **Forgot to update Cursor deeplink**: Base64 config becomes stale
- **Path changes not propagated**: Users get file not found errors
- **New env vars missing**: Client setup fails silently
- **Command changes not updated**: Installation instructions become outdated

**Always run `scripts/validate-configs.py` before submitting PRs that touch server configuration!**