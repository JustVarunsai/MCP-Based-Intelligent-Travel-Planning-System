import json

from mcp_server._app import mcp
from mcp_server.tools.destinations import search_destinations


@mcp.resource("travel://destinations/{name}", mime_type="application/json")
def destination_guide(name: str) -> str:
    """Wikivoyage-backed travel guide for the named destination."""
    fn = search_destinations.fn if hasattr(search_destinations, "fn") else search_destinations
    result = fn(query=name)
    return json.dumps(result, ensure_ascii=False)
