# Capsule CRM MCP Example

This repository contains a minimal [Model Context Protocol](https://github.com/antora) server exposing read only Capsule CRM tools.  It allows AI assistants such as Claude Desktop to list and search your Capsule data without giving write access.

## Available Tools

The MCP server provides the following Capsule CRM tools:

### `list_contacts`
Returns a paginated list of contacts from your Capsule CRM.
- **Parameters:**
  - `page` (optional): Page number, defaults to 1
  - `per_page` (optional): Number of contacts per page, defaults to 50
  - `archived` (optional): Include archived contacts, defaults to false

### `search_contacts` 
Fuzzy search for contacts by name, email, or organisation.
- **Parameters:**
  - `keyword` (required): Search term to find contacts
  - `page` (optional): Page number, defaults to 1  
  - `per_page` (optional): Number of results per page, defaults to 50

### `list_open_opportunities`
Returns open sales opportunities ordered by expected close date.
- **Parameters:**
  - `page` (optional): Page number, defaults to 1
  - `per_page` (optional): Number of opportunities per page, defaults to 50

**Example queries you can ask Claude Desktop:**
- "List my Capsule contacts"
- "Search for contacts with email domain @example.com"
- "Show me open opportunities closing this month"
- "Find contacts named John"

## Prerequisites

* Python 3.10+
* A Capsule CRM API token (create one in Capsule under *My Preferences → API Authentication*)

### Environment Setup

**For Claude Desktop usage:** No `.env` file needed - the token is configured directly in `claude_desktop_config.json`.

**For standalone development/testing:** Copy `.env.example` to `.env` and add your token:

```bash
cp .env.example .env
# edit .env and set CAPSULE_API_TOKEN=your_token_here
```

## Installation

Create a virtual environment and install the package:

```bash
python -m venv venv
source venv/bin/activate
pip install -e .
```

## Running the server

Start the server with Uvicorn:

```bash
uvicorn capsule_mcp.server:app --reload
```

The API will be available at `http://localhost:8000/mcp/`.

## Using with Claude Desktop

Add the server to your Claude Desktop configuration file (`claude_desktop_config.json`):

**Location:** 
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "capsule-crm": {
      "command": "uvicorn",
      "args": [
        "capsule_mcp.server:app",
        "--host", "0.0.0.0",
        "--port", "8000"
      ],
      "env": {
        "CAPSULE_API_TOKEN": "your_capsule_api_token_here"
      }
    }
  }
}
```

Alternatively, if you prefer to run the server manually and connect via HTTP:

```json
{
  "mcpServers": {
    "capsule-crm": {
      "command": "python",
      "args": [
        "/absolute/path/to/your/capsule-crm-mcp-server/capsule_mcp/server.py"
      ],
      "env": {
        "CAPSULE_API_TOKEN": "your_capsule_api_token_here"
      }
    }
  }
}
```

**Important:** Replace `/absolute/path/to/your/capsule-crm-mcp-server/` with the actual path to this repository on your system.

Restart Claude Desktop and you can issue commands like "List my Capsule contacts".

## Testing

Run the test suite with `pytest`:

```bash
python -m pytest
```

Manually test the server with `curl`

Test the schema endpoint
```bash
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
  }'
```

Test listing contacts
```bash
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "list_contacts",
      "arguments": {"page": 1, "per_page": 10}
    },
    "id": 1
  }'
```
