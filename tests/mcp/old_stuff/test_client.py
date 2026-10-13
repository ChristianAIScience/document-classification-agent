
import asyncio
# Achte auf die Großschreibung: MCPToolset
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams


async def main():
    # Initialisierung des Toolsets
    toolset = McpToolset(
        connection_params=StreamableHTTPConnectionParams(
            # FastMCP Server hängen oft /mcp an die URL an
            url="http://localhost:8001/mcp" 
        )
    )

    try:
        # Tools abrufen (Discovery)
        tools = await toolset.get_tools()
        
        print(f"Gefundene Tools: {len(tools)}")
        for tool in tools:
            print(f"- Tool Name: {tool.name}")
            print(f"- Beschreibung: {tool.description}")

    except Exception as e:
        print(f"Fehler beim Verbinden: {e}")


if __name__ == "__main__":
    asyncio.run(main())
