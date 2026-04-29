"""Config for the custom MCP travel server."""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # transport
    HOST = os.getenv("MCP_HOST", "0.0.0.0")
    PORT = int(os.getenv("MCP_PORT", "8000"))

    # auth — shared secret for SSE; clients send X-MCP-Token header
    AUTH_TOKEN = os.getenv("MCP_AUTH_TOKEN", "")

    # third-party API keys (none needed for our free travel APIs)
    USER_AGENT = os.getenv("MCP_USER_AGENT", "travel-mcp/0.1")

    # rate-limit minimum gap between Nominatim/OSRM calls (seconds)
    OSM_MIN_GAP_SECONDS = float(os.getenv("OSM_MIN_GAP", "1.1"))

    # cache size for geocoding LRU
    GEOCODE_CACHE_SIZE = int(os.getenv("GEOCODE_CACHE_SIZE", "512"))


config = Config()
