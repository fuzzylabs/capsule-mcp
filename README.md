# Capsule CRM MCP Server

A Model Context Protocol (MCP) server for Capsule CRM, allowing AI assistants to interact with your Capsule CRM data.

## Features

- List and search contacts
- Create new contacts
- Add notes to contacts
- List open opportunities
- Secure API token management
- Environment-based configuration

## Prerequisites

- Python 3.8 or higher
- A Capsule CRM account
- A Capsule CRM API token

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/fuzzylabs/capsule-crm-mcp-server.git
   cd capsule-crm-mcp-server
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install the package in development mode:
   ```bash
   # Install with development dependencies
   pip install -e ".[dev]"
   ```

4. Create a `.env` file in the project root:
   ```bash
   CAPSULE_API_TOKEN=your_api_token_here
   ```

## Running the Server

Start the server with:
```bash
uvicorn capsule_mcp.server:app --reload
```

The server will be available at `http://localhost:8000`.

## Testing

The project includes a comprehensive test suite to ensure reliability and functionality. Tests are written using pytest and include both unit and integration tests.

### Running Tests

To run the test suite:

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run a specific test file
pytest tests/test_server.py

# Run a specific test
pytest tests/test_server.py::test_list_contacts
```

### Test Coverage

The test suite covers:
- MCP schema validation
- All MCP tools functionality
- Error handling
- API response validation
- Input validation

### Writing Tests

When adding new features, please include corresponding tests. The test suite uses:
- `pytest` for test framework
- `pytest-asyncio` for async test support
- `TestClient` from FastAPI for API testing
- Mocking for external API calls

Example test structure:
```python
def test_feature_name(client, mock_capsule_response):
    """Test description."""
    response = client.post(
        "/mcp",
        json={
            "type": "tool",
            "tool": "tool_name",
            "args": {"arg1": "value1"},
        },
    )
    assert response.status_code == 200
    # Add more assertions as needed
```

### Development Setup

For development work, install the package in development mode with all dependencies:
```bash
pip install -e ".[dev]"
```

This will install:
- The package in editable mode
- All runtime dependencies
- Development dependencies (pytest, pytest-asyncio)

## Configuring MCP Clients

### Claude Desktop

1. Edit the Claude Desktop configuration file:
   - macOS: `~/Library/Application Support/claude-desktop/config.json`
   - Windows: `%APPDATA%\claude-desktop/config.json`
   - Linux: `~/.config/claude-desktop/config.json`

2. Add the MCP server configuration:
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

3. Restart Claude Desktop to apply the changes.

4. Try it out with prompts like:
   - "List my open opportunities"
   - "Search for contacts with 'john' in their name"
   - "Add a note to contact ID 123"

## API Documentation

Once the server is running, you can access the API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Security Considerations

- The API token is stored in environment variables
- All API requests are made over HTTPS
- Input validation is performed on all requests
- Rate limiting is implemented to prevent abuse

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
