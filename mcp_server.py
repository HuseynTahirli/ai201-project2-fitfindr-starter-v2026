"""
FitFindr MCP server. Exposes search_listings so any MCP client can call it.

    python mcp_server.py        starts the server (it will just sit there)
    python mcp_client.py        asks the server what it offers
"""

from mcp.server.fastmcp import FastMCP

from tools import search_listings as _search_listings_impl

mcp = FastMCP("fitfindr", log_level="WARNING")


@mcp.tool()
def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search secondhand clothing listings by text description. Optionally filter
    by size (for example "M" or "L") and max_price, in whole dollars. Returns
    a list of matching listings, each a dict with the listing's fields.
    Returns an empty list if nothing matches.
    """
    return _search_listings_impl(description, size, max_price)


if __name__ == "__main__":
    mcp.run()