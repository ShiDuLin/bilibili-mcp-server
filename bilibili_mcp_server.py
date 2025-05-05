from fastmcp import FastMCP
from bilibili_api import search

mcp = FastMCP("Bilibili Mcp Server")


@mcp.tool()
async def general_search(keyword: str) -> dict:
    """
    search Bilibili API with the given keyword.

    Args:
        keyword (str): search term to look for on Bilibili API.
    Returns:
        dict containing thr search results from Bilibili API.
    """
    return await search.search(keyword)


if __name__ == "__main__":
    mcp.run()
