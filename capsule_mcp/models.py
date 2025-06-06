"""Data models for the Capsule CRM MCP server."""

from pydantic import BaseModel

class NewPerson(BaseModel):
    first_name: str
    last_name: str
    email: str | None = None
    organisation: str | None = None
    tags: list[str] | None = None 