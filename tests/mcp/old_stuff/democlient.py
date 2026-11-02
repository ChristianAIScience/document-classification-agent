import asyncio
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


async def example():
    transport = StreamableHttpTransport("http://127.0.0.1:8000/mcp/")
    async with Client(transport=transport) as client:
        await client.ping()
        print("Ping successful! 🚀")

        # List available tools to confirm greet is available
        tools = await client.list_tools()
        print("💵💵💵💵💵")
        print("Available tools:", tools)
        print("🚀🚀🚀🚀🚀")
        greeting = await client.call_tool("greet", {"name": "Bob"})
        print("greeting result", greeting)


if __name__ ==  "__main__":
    asyncio.run(example())
