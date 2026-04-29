"""
MCP Resource: destination guides as readable URIs.

URI:    travel://destinations/{name}
Format: JSON with cleaned Wikivoyage section text.
Demonstrates the parameterised-resource pattern in MCP.
"""
import json

from mcp_server._app import mcp
from mcp_server.tools.destinations import search_destinations


@mcp.resource("travel://destinations/{name}", mime_type="application/json")
def destination_guide(name: str) -> str:
    """Wikivoyage-backed travel guide for the named destination."""
    # delegate to the existing tool — same data, just exposed as a resource URI
    result = search_destinations.fn(query=name) if hasattr(search_destinations, "fn") else search_destinations(name)
    return json.dumps(result, ensure_ascii=False)
