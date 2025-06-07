# Capsule CRM MCP Example

This repository contains a minimal [Model Context Protocol](https://github.com/antora) server exposing read only Capsule CRM tools.  It allows AI assistants such as Claude Desktop to list and search your Capsule data without giving write access.

## Prerequisites

* Python 3.10+
* A Capsule CRM API token (create one in Capsule under *My Preferences → API Authentication*)

Copy `.env.example` to `.env` and paste your token:

```bash
cp .env.example .env
# edit .env and set CAPSULE_API_TOKEN
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

The API will be available at `http://localhost:8000/mcp`.

## Using with Claude Desktop

Add the server to your Claude Desktop configuration file (`config.json`):

```json
{
  "mcpServers": [
    {"name": "Capsule CRM", "url": "http://localhost:8000/mcp"}
  ]
}
```

Restart Claude Desktop and you can issue commands like "List my Capsule contacts".

## Testing

Run the test suite with `pytest`:

```bash
python -m pytest
```

Manually test the server with `curl`

Test the schema endpoint
```
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"type": "schema"}'
```

Test listing contacts
```curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "type": "tool",
    "tool": "list_contacts",
    "args": {
      "page": 1,
      "per_page": 10
    }
  }'
```