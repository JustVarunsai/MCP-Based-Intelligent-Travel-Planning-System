import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    HOST = os.getenv("MCP_HOST", "0.0.0.0")
    PORT = int(os.getenv("MCP_PORT", "8000"))
    AUTH_TOKEN = os.getenv("MCP_AUTH_TOKEN", "")
    USER_AGENT = os.getenv(
        "MCP_USER_AGENT",
        "travel-mcp/0.1 (https://github.com/JustVarunsai; college-project) python-httpx",
    )
    OSM_MIN_GAP_SECONDS = float(os.getenv("OSM_MIN_GAP", "1.1"))
    GEOCODE_CACHE_SIZE = int(os.getenv("GEOCODE_CACHE_SIZE", "512"))


config = Config()
