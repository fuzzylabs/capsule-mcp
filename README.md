# Capsule CRM MCP Server

A minimal **Model Context Protocol** server that exposes Capsule CRM endpoints
as AI-accessible tools.

## Quick Start

```bash
git clone git@github.com:fuzzylabs/capsule-crm-mcp-server.git
cd capsule-crm-mcp-server
python -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
# or: pip install .
export CAPSULE_API_TOKEN="<your-personal-access-token>"
uvicorn capsule_mcp.server:mcp --reload --port 8000
```

Open [http://localhost:8000/mcp](http://localhost:8000/mcp) in a browser to
see the MCP discovery document, or register that URL in any MCP-enabled AI
client (Claude, VS Code Copilot Chat, Anthropic Console, etc.).

## Endpoints Exposed

| Tool | Description |
|------|-------------|
| `list_contacts` | Paginated list of contacts |
| `search_contacts` | Fuzzy search contacts |
| `create_person` | Create a new **person** contact |
| `add_note` | Attach a note to a contact |
| `list_open_opportunities` | List open sales opportunities |

## Extending

Just add another `@mcp.tool`‑decorated async function that calls the Capsule
REST API – it will automatically appear in the MCP schema.

## Packaging

This repo is **PEP 517/518** compliant (`pyproject.toml`). After cloning you
can install locally with:

```bash
pip install -e .
```

or build a wheel:

```bash
python -m build
```

## License

MIT – see `LICENSE`.
