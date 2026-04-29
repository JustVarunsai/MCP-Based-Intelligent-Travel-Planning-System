"""
Shared factories for the model and MCP tool connections.
"""
from agno.tools.mcp import MCPTools
from agno.models.openai import OpenAIChat
from config import config


def create_model():
    """LLM instance shared across all agents."""
    return OpenAIChat(id=config.OPENAI_MODEL, api_key=config.openai_api_key)


def create_airbnb_mcp():
    """Airbnb MCP server — spawns a local npx process."""
    return MCPTools(
        command=config.AIRBNB_MCP_CMD,
        timeout_seconds=config.MCP_TIMEOUT,
    )
