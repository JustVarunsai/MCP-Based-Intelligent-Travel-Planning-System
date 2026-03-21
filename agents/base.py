"""
Shared factories for the model and MCP tool connections.
Each agent that needs an MCP server gets its own MCPTools instance
so connections stay isolated.
"""
import os
from agno.tools.mcp import MCPTools
from agno.models.openai import OpenAIChat
from config import config


def create_model():
    """GPT-4o model instance shared across all agents."""
    return OpenAIChat(id=config.OPENAI_MODEL, api_key=config.openai_api_key)


def create_airbnb_mcp():
    """Airbnb MCP server — spawns a local npx process."""
    return MCPTools(
        command=config.AIRBNB_MCP_CMD,
        timeout_seconds=config.MCP_TIMEOUT,
    )


def create_google_maps_mcp():
    """Google Maps MCP server — needs the Maps API key in env."""
    os.environ["GOOGLE_MAPS_API_KEY"] = config.google_maps_key
    return MCPTools(
        command=config.MAPS_MCP_CMD,
        env={"GOOGLE_MAPS_API_KEY": config.google_maps_key},
        timeout_seconds=config.MCP_TIMEOUT,
    )
