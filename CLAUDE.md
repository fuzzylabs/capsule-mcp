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