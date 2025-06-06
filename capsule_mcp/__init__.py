"""Capsule MCP package – import *app* to get the FastAPI application."""

from .server import app, mcp
from .models import NewPerson

__all__ = ["app", "mcp", "NewPerson"]

__version__ = "0.1.0"
