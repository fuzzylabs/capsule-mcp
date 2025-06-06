# Capsule CRM MCP Server

A minimal **Model Context Protocol** server that exposes Capsule CRM endpoints
as AI-accessible tools.

## Prerequisites

- Python 3.10 or later
- A Capsule CRM account with API access
- A personal access token from Capsule CRM

## Quick Start

1. Clone the repository:
   ```bash
   git clone git@github.com/fuzzylabs/capsule-crm-mcp-server.git
   cd capsule-crm-mcp-server
   ```

2. Create and activate a virtual environment:
   ```bash
   # Using venv (recommended)
   python -m venv .venv
   source .venv/bin/activate  # On Unix/macOS
   # or
   .venv\Scripts\activate  # On Windows
   ```

3. Install dependencies:
   ```bash
   pip install -U pip
   pip install -r requirements.txt
   # or install in development mode:
   pip install -e .
   ```

4. Set up your Capsule CRM API token:
   ```bash
   # Create a .env file
   echo "CAPSULE_API_TOKEN=your-token-here" > .env
   ```
   You can create a personal access token in Capsule CRM:
   1. Go to My Preferences → API Authentication
   2. Click "Create New Personal Access Token"
   3. Copy the token and paste it in your `.env` file

5. Start the server:
   ```bash
   uvicorn capsule_mcp.server:mcp --reload --port 8000
   ```

## Available Tools

The server exposes the following Capsule CRM operations as MCP tools:

| Tool | Description |
|------|-------------|
| `list_contacts` | Get a paginated list of contacts |
| `search_contacts` | Fuzzy search contacts by name, email, or organisation |
| `create_person` | Create a new person contact |
| `add_note` | Attach a note to a contact |
| `list_open_opportunities` | List open sales opportunities |

## Configuring MCP Clients

### Cursor

You can add this MCP server to Cursor in two ways:

1. **Quick Add (Recommended)**
   - Click the [Add to Cursor](add-to-cursor.html) button
   - This will automatically open Cursor and add the server to your settings

2. **Manual Setup**
   - Open Cursor's settings:
     - macOS: `Cmd + ,`
     - Windows/Linux: `Ctrl + ,`
   - Search for "MCP" in the settings search bar
   - Under "MCP Servers", click "Add Server" and enter:
     - Name: `Capsule CRM`
     - URL: `http://localhost:8000/mcp`
   - Click "Save" and restart Cursor

You can now use Cursor to interact with your Capsule CRM data. Try asking questions like:
- "List my open opportunities"
- "Search for contacts with 'Acme' in their name"
- "Create a new contact for John Smith at Acme Corp"

### Claude Desktop

1. Locate your Claude Desktop configuration file:
   - macOS: `~/Library/Application Support/claude-desktop/config.json`
   - Windows: `%APPDATA%\claude-desktop\config.json`
   - Linux: `~/.config/claude-desktop/config.json`

2. Edit the configuration file to add the MCP server:
   ```json
   {
     "mcpServers": [
       {
         "name": "Capsule CRM",
         "url": "http://localhost:8000/mcp"
       }
     ]
   }
   ```

3. Save the file and restart Claude Desktop

You can now use Claude Desktop to interact with your Capsule CRM data. Try asking questions like:
- "List my open opportunities"
- "Search for contacts with 'Acme' in their name"
- "Create a new contact for John Smith at Acme Corp"

### VS Code Copilot Chat

1. Open VS Code settings
2. Search for "Copilot Chat: MCP Servers"
3. Add a new server:
   ```json
   {
     "name": "Capsule CRM",
     "url": "http://localhost:8000/mcp"
   }
   ```

### Anthropic Console

1. Go to the Anthropic Console
2. Click on "Settings"
3. Under "MCP Servers", add:
   ```
   http://localhost:8000/mcp
   ```

### Claude API

When making API calls, include the MCP server URL in your request:
```python
import anthropic

client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=1000,
    messages=[{"role": "user", "content": "List my open opportunities"}],
    mcp_servers=["http://localhost:8000/mcp"]
)
```

## Development

### Installing Development Dependencies

```bash
pip install -e ".[dev]"
```

This installs additional tools for development:
- `black` for code formatting
- `isort` for import sorting
- `pytest` for testing
- `ruff` for linting

### Running Tests

```bash
pytest
```

### Code Style

The project uses:
- Black for code formatting
- isort for import sorting
- ruff for linting

To format your code:
```bash
black .
isort .
ruff check .
```

## License

MIT – see `LICENSE`.
