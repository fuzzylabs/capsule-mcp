"""Capsule MCP package – import *mcp* to get the FastMCP application."""

from .server import mcp
from .models import NewPerson

__all__ = ["mcp", "NewPerson"]
