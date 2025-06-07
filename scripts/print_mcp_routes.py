from capsule_mcp.server import mcp

app = mcp.http_app()

print('ROUTES:', [(route.path, getattr(route, 'methods', None)) for route in app.routes]) 