"""
config.py

Loads and validates environment configuration from .env file.
"""

import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN: str = os.environ.get("GITHUB_TOKEN", "")
SALESFORCE_CODEBASE_PATH: str = os.environ.get("SALESFORCE_CODEBASE_PATH", "")
MODEL: str = os.environ.get("MODEL", "claude-sonnet-4-5")

# Lucid MCP server — uses mcp-remote to bridge OAuth-authenticated HTTP → stdio
LUCID_MCP_COMMAND: str = os.environ.get("LUCID_MCP_COMMAND", "npx")
LUCID_MCP_ARGS: list[str] = os.environ.get(
    "LUCID_MCP_ARGS", "-y mcp-remote https://mcp.lucid.app/mcp"
).split()


def resolve_github_token(session_env: dict | None = None) -> str:
    """Resolve GitHub token from Chainlit user env first, then .env fallback."""
    if isinstance(session_env, dict):
        token = str(session_env.get("GITHUB_TOKEN", "")).strip()
        if token:
            return token
    return GITHUB_TOKEN.strip()
