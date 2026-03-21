import os
import streamlit as st


def get_key(name, default=""):
    """Pull a key from session state first, then env vars."""
    val = st.session_state.get(name, "")
    if val:
        return val
    return os.getenv(name, default)


class Config:
    # --- LLM ---
    OPENAI_MODEL = "gpt-4o"
    EMBEDDING_MODEL = "text-embedding-3-small"
    EMBEDDING_DIMENSIONS = 1536

    # --- MCP server commands ---
    AIRBNB_MCP_CMD = "npx -y @openbnb/mcp-server-airbnb --ignore-robots-txt"
    MAPS_MCP_CMD = "npx @gongrzhe/server-travelplanner-mcp"
    MCP_TIMEOUT = 60  # seconds

    # --- Pinecone ---
    PINECONE_INDEX = "travel-knowledge"
    PINECONE_CLOUD = "aws"
    PINECONE_REGION = "us-east-1"

    @property
    def openai_api_key(self):
        return get_key("OPENAI_API_KEY")

    @property
    def google_maps_key(self):
        return get_key("GOOGLE_MAPS_API_KEY")

    @property
    def pinecone_api_key(self):
        return get_key("PINECONE_API_KEY")

    @property
    def supabase_url(self):
        return get_key("SUPABASE_URL")

    @property
    def supabase_key(self):
        return get_key("SUPABASE_KEY")


config = Config()
