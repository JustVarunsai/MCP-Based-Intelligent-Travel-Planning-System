import os
from dotenv import load_dotenv
import streamlit as st

# load .env if present
load_dotenv()


def get_key(name, default=""):
    """Pull a key from session state first, then env vars."""
    try:
        val = st.session_state.get(name, "")
    except Exception:
        val = ""
    if val:
        return val
    return os.getenv(name, default)


class Config:
    # --- LLM ---
    OPENAI_MODEL = "gpt-4o-mini"

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
    def database_url(self):
        return get_key("SUPABASE_DATABASE_URL")

    @property
    def serper_api_key(self):
        return get_key("SERPER_API_KEY")


config = Config()
