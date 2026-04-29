import os
import sys
from dotenv import load_dotenv

load_dotenv()


class Config:
    OPENAI_MODEL = "gpt-4o-mini"

    MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "")
    MCP_AUTH_TOKEN = os.getenv("MCP_AUTH_TOKEN", "")
    MCP_STDIO_COMMAND = os.getenv(
        "MCP_STDIO_COMMAND",
        f"{sys.executable} -m mcp_server.server",
    )
    MCP_TIMEOUT = int(os.getenv("MCP_TIMEOUT", "60"))

    PINECONE_INDEX = os.getenv("PINECONE_INDEX", "travel-knowledge")
    PINECONE_CLOUD = os.getenv("PINECONE_CLOUD", "aws")
    PINECONE_REGION = os.getenv("PINECONE_REGION", "us-east-1")

    @property
    def openai_api_key(self) -> str:
        return os.getenv("OPENAI_API_KEY", "")

    @property
    def pinecone_api_key(self) -> str:
        return os.getenv("PINECONE_API_KEY", "")

    @property
    def database_url(self) -> str:
        return os.getenv("SUPABASE_DATABASE_URL", "")

    @property
    def use_sse(self) -> bool:
        return bool(self.MCP_SERVER_URL)


config = Config()
