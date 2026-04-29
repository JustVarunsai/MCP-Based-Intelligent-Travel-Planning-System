"""
Shared factories for the LLM and the custom MCP travel server connection.
"""
from agno.tools.mcp import MCPTools
from agno.models.openai import OpenAIChat
from backend.config import config


def create_model():
    """LLM instance shared across all agents."""
    return OpenAIChat(id=config.OPENAI_MODEL, api_key=config.openai_api_key)


def create_travel_mcp() -> MCPTools:
    """
    Create an MCPTools client for our custom travel MCP server.

    - If MCP_SERVER_URL is set, connect via SSE/HTTP (cloud or remote dev).
    - Otherwise, spawn the server as a local stdio subprocess.

    Caller is responsible for the async lifecycle (use as `async with ...`).
    """
    if config.use_sse:
        headers = {}
        if config.MCP_AUTH_TOKEN:
            headers["X-MCP-Token"] = config.MCP_AUTH_TOKEN
        return MCPTools(
            transport="sse",
            url=config.MCP_SERVER_URL,
            headers=headers or None,
            timeout_seconds=config.MCP_TIMEOUT,
        )
    return MCPTools(
        command=config.MCP_STDIO_COMMAND,
        timeout_seconds=config.MCP_TIMEOUT,
    )
