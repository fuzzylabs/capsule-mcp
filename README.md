# Capsule CRM MCP Server

> **Connect your Capsule CRM data to AI assistants** — Access contacts, opportunities, support cases, and more through natural language queries, with complete read-only security.

[![Model Context Protocol](https://img.shields.io/badge/MCP-Compatible-blue)](https://modelcontextprotocol.io) [![Python 3.10+](https://img.shields.io/badge/Python-3.10+-green)](https://python.org) [![Capsule CRM API v2](https://img.shields.io/badge/Capsule%20CRM-API%20v2-orange)](https://developer.capsulecrm.com)

**🚨 Disclaimer**: This project is created by [Fuzzy Labs](https://fuzzylabs.ai) with good vibes and is not officially supported by Capsule CRM. Use at your own discretion.

## What This Does

Transform how you work with your Capsule CRM data by asking AI assistants natural language questions like:

- *"Show me my recent contacts"*
- *"What opportunities are closing this month?"* 
- *"Find all support cases from last week"*
- *"List tasks assigned to Sarah"*
- *"What products do we sell in the UK?"*

**🔒 Read-Only & Secure** — No write access to your CRM data  
**🚀 Instant Setup** — Works with any MCP-compatible AI assistant  
**📊 Complete Coverage** — Access contacts, sales, support, tasks, projects & more

## Quick Start

### 1. Get Your Capsule API Token
1. Log into your Capsule CRM account
2. Go to **My Preferences → API Authentication**
3. Create a new API token and copy it

### 2. Install & Configure

#### macOS Setup

```bash
# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install
git clone https://github.com/fuzzylabs/capsule-mcp.git
cd capsule-mcp
uv sync
```

#### Linux/Windows Setup

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh  # Linux/macOS
# OR for Windows: powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Clone and install
git clone https://github.com/fuzzylabs/capsule-mcp.git
cd capsule-mcp
uv sync
```

### 3. Connect to Your AI Assistant

#### Claude Desktop

Add this to your Claude Desktop config file:

**Config Location:**
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "capsule-crm": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/your/capsule-mcp",
        "python",
        "capsule_mcp/server.py"
      ],
      "env": {
        "CAPSULE_API_TOKEN": "your_capsule_api_token_here"
      }
    }
  }
}
```

#### Cursor

**📋 Quick Setup:** 

<a href="cursor://anysphere.cursor-deeplink/mcp/install?name=capsule-crm&config=eyJjYXBzdWxlLWNybSI6eyJjb21tYW5kIjoidXYiLCJhcmdzIjpbInJ1biIsIi0tZGlyZWN0b3J5IiwiL3BhdGgvdG8veW91ci9jYXBzdWxlLW1jcCIsInB5dGhvbiIsImNhcHN1bGVfbWNwL3NlcnZlci5weSJdLCJlbnYiOnsiQ0FQU1VMRV9BUElfVE9LRU4iOiJ5b3VyX2NhcHN1bGVfYXBpX3Rva2VuX2hlcmUifX19" style="display: inline-block; background-color: #007AFF; color: white; padding: 10px 20px; text-decoration: none; border-radius: 6px; font-weight: 500;">🚀 Add to Cursor (One-Click Install)</a>

**Note:** After clicking the button, you'll need to:
1. Update the path `/path/to/your/capsule-mcp` to your actual installation directory
2. Replace `your_capsule_api_token_here` with your actual Capsule CRM API token

Or manually add this to your Cursor MCP settings:

```json
{
  "capsule-crm": {
    "command": "uv",
    "args": [
      "run",
      "--directory",
      "/path/to/your/capsule-mcp",
      "python",
      "capsule_mcp/server.py"
    ],
    "env": {
      "CAPSULE_API_TOKEN": "your_capsule_api_token_here"
    }
  }
}
```

#### Other MCP Clients

This server is compatible with any MCP client. Refer to your client's documentation for MCP server configuration.

**💡 Setup Help:**
- **Using uv (recommended):** Use `uv run` command as shown above - no Python path needed!
- **uv path for Claude Desktop:** Use full path `~/.local/bin/uv` (find yours with `which uv`)
- **Manual Python paths (if not using uv):**
  - **macOS (Homebrew):** `/opt/homebrew/bin/python3` (Apple Silicon) or `/usr/local/bin/python3` (Intel)
  - **macOS (System):** `/usr/bin/python3` (if available)
  - **Find your Python:** Run `which python3` in terminal
  - **Windows:** Try `C:\Python311\python.exe`

### 4. Start Using

1. **Restart your AI assistant**
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
- **Using uv:** Make sure you're using the absolute directory path with `uv run --directory`
- **Manual setup:** Verify Python can find the installed packages: `pip list | grep fastmcp`

**"spawn uv ENOENT" or "command not found: uv"**
- Install uv first: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Restart your terminal after installation
- Verify installation: `uv --version`

**"spawn python ENOENT" (if not using uv)**
- Switch to uv setup (recommended) or use full Python path in config
- Check your Python path: `which python3`
- Try different common paths: `/usr/bin/python3`, `/usr/local/bin/python3`, `/opt/homebrew/bin/python3`

**"Authentication failed"**
- Verify your Capsule API token is correct
- Check the token has appropriate permissions in Capsule CRM

**MCP tools not showing in your AI assistant**
- Restart your AI assistant after config changes
- Check the config file syntax is valid JSON
- Verify file paths are absolute, not relative

### Getting Help

- **Issues & Bugs:** [GitHub Issues](https://github.com/fuzzylabs/capsule-mcp/issues)
- **Capsule API Docs:** [developer.capsulecrm.com](https://developer.capsulecrm.com)
- **MCP Protocol:** [modelcontextprotocol.io](https://modelcontextprotocol.io)

---

## Render Deployment (Secure Remote HTTP Access)

Want to deploy the MCP server remotely so multiple users can access it via HTTP? Deploy to Render for easy cloud hosting with API key authentication.

### Quick Deploy

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/fuzzylabs/capsule-mcp)

### Manual Deployment

1. **Fork this repository** to your GitHub account

2. **Create a Render account** at [render.com](https://render.com)

3. **Create a new Web Service** and connect your GitHub fork

4. **Configure the service:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn capsule_mcp.server:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free (or choose a paid plan for better performance)

5. **Set environment variables** in Render dashboard:
   - `CAPSULE_API_TOKEN`: Your Capsule CRM API token
   - `MCP_API_KEY`: A secure random API key for authentication (see generation instructions below)

6. **Deploy** - Render will automatically build and deploy your service

### Generating a Secure API Key

Generate a secure random API key for the `MCP_API_KEY` environment variable:

```bash
# Using Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Using OpenSSL  
openssl rand -base64 32

# Using Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"
```

⚠️ **Important**: Store this API key securely - you'll need it to configure your MCP clients.

### Using Your Deployed Server

Once deployed, you'll get a URL like `https://your-service.onrender.com`. Configure your MCP clients to use:

**Claude Desktop:**
```json
{
  "mcpServers": {
    "capsule-crm": {
      "command": "curl",
      "args": [
        "-X", "POST",
        "https://your-service.onrender.com/mcp/",
        "-H", "Content-Type: application/json",
        "-H", "Authorization: Bearer YOUR_MCP_API_KEY_HERE",
        "-d", "@-"
      ]
    }
  }
}
```

Replace `YOUR_MCP_API_KEY_HERE` with the API key you generated and set in Render.

🔒 **Security Note**: The API key authentication is only enforced when the `MCP_API_KEY` environment variable is set. If no API key is configured, the server will accept unauthenticated requests (useful for local development).

**Direct HTTP Access:**
```bash
# List available tools
curl -X POST https://your-service.onrender.com/mcp/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_MCP_API_KEY_HERE" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}'

# List contacts
curl -X POST https://your-service.onrender.com/mcp/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_MCP_API_KEY_HERE" \
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

**⚠️ Note on Free Tier:** Render's free tier spins down services after inactivity. First requests may take 30-60 seconds to wake up the service.

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
uv run pytest
```

**HTTP Server (for testing):**
```bash
uv run uvicorn capsule_mcp.server:app --reload
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
