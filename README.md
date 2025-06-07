# Capsule CRM + Claude Desktop Integration

> **Connect your Capsule CRM data directly to Claude Desktop** — Access contacts, opportunities, support cases, and more through natural language queries, with complete read-only security.

[![Model Context Protocol](https://img.shields.io/badge/MCP-Compatible-blue)](https://modelcontextprotocol.io) [![Python 3.10+](https://img.shields.io/badge/Python-3.10+-green)](https://python.org) [![Capsule CRM API v2](https://img.shields.io/badge/Capsule%20CRM-API%20v2-orange)](https://developer.capsulecrm.com)

## What This Does

Transform how you work with your Capsule CRM data by asking Claude Desktop natural language questions like:

- *"Show me my recent contacts"*
- *"What opportunities are closing this month?"* 
- *"Find all support cases from last week"*
- *"List tasks assigned to Sarah"*
- *"What products do we sell in the UK?"*

**🔒 Read-Only & Secure** — No write access to your CRM data  
**🚀 Instant Setup** — Works with Claude Desktop in minutes  
**📊 Complete Coverage** — Access contacts, sales, support, tasks, projects & more

## Quick Start

### 1. Get Your Capsule API Token
1. Log into your Capsule CRM account
2. Go to **My Preferences → API Authentication**
3. Create a new API token and copy it

### 2. Install & Configure

```bash
# Clone and install
git clone https://github.com/fuzzylabs/capsule-mcp.git
cd capsule-mcp
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

### 3. Connect to Claude Desktop

Add this to your Claude Desktop config file:

**Config Location:**
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "capsule-crm": {
      "command": "/usr/bin/python3",
      "args": [
        "/path/to/your/capsule-mcp/capsule_mcp/server.py"
      ],
      "env": {
        "CAPSULE_API_TOKEN": "your_capsule_api_token_here"
      }
    }
  }
}
```

**💡 Python Path Help:**
- **Find your Python:** Run `which python3` in terminal
- **Using pyenv:** Use full path from `pyenv which python`
- **Windows:** Try `C:\Python311\python.exe`

### 4. Start Using

1. **Restart Claude Desktop**
2. **Start asking questions!**

Try these example queries:
> *"List my Capsule contacts"*  
> *"Show me open opportunities closing this month"*  
> *"What support cases need attention?"*  
> *"Find contacts from @example.com"*

## What You Can Access

This MCP server provides **complete read-only access** to your Capsule CRM:

| **Data Type** | **What You Can Do** |
|---------------|-------------------|
| **👥 Contacts** | List, search, view details, find recent activity |
| **💼 Sales** | View opportunities, pipeline stages, sales forecasts |
| **🎫 Support** | Access cases, search issues, track resolution |
| **✅ Tasks** | View task lists, assignments, deadlines |
| **📝 Timeline** | Read notes, emails, calls, meeting records |
| **📋 Projects** | Access project data and status |
| **🏷️ Organization** | View tags, users, custom fields, configuration |
| **🛍️ Products** | Browse product catalog and categories |

**➡️ [View Complete Tool Reference](TOOLS.md)**

## Troubleshooting

### Common Issues

**"No module named 'capsule_mcp'"**
- Make sure you're using the absolute path to the server.py file
- Verify Python can find the installed packages: `pip list | grep fastmcp`

**"spawn python ENOENT"**
- Check your Python path is correct: `which python3`
- Use the full path (e.g., `/usr/bin/python3` not just `python3`)

**"Authentication failed"**
- Verify your Capsule API token is correct
- Check the token has appropriate permissions in Capsule CRM

**Claude Desktop not showing MCP tools**
- Restart Claude Desktop after config changes
- Check the config file syntax is valid JSON
- Verify file paths are absolute, not relative

### Getting Help

- **Issues & Bugs:** [GitHub Issues](https://github.com/fuzzylabs/capsule-mcp/issues)
- **Capsule API Docs:** [developer.capsulecrm.com](https://developer.capsulecrm.com)
- **MCP Protocol:** [modelcontextprotocol.io](https://modelcontextprotocol.io)

---

## For Developers

### Development Setup

**Environment Variables (for development):**
```bash
cp .env.example .env
# Edit .env and set CAPSULE_API_TOKEN=your_token_here
```

**Run Tests:**
```bash
python -m pytest
```

**HTTP Server (for testing):**
```bash
uvicorn capsule_mcp.server:app --reload
# Server available at http://localhost:8000/mcp/
```

### API Testing

Test the schema endpoint:
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

Test listing contacts:
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

### Architecture

- **Server:** FastMCP framework with FastAPI backend
- **Protocol:** Model Context Protocol (MCP) via stdio
- **API:** Capsule CRM API v2 with read-only access
- **Authentication:** Bearer token (OAuth2)
