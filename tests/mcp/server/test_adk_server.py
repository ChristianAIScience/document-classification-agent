import json

import asyncio
import logging
import os

from fastmcp import FastMCP

logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

mcp = FastMCP(name="Test MCP Server 💵", json_response=True)


@mcp.tool
async def greet(name: str) -> str:
    """Greet a user by name"""
    return f"Hello: {name}"


if __name__ == "__main__":
    logger.info(f"🚀 MCP server started on port {os.getenv('PORT', 8080)}")
    asyncio.run(
        mcp.run_async(transport="http",
                      host="0.0.0.0",
                      port=os.getenv("PORT", 8080))
                      )
    