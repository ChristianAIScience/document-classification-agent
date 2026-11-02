
import logging
import os

from dotenv import load_dotenv

from google.adk.agents import Agent
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams


logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

load_dotenv()

SYSTEM_INSTRUCTION = (
    "You are a specialized assistant for calculating power data."
    "Do not attempt to answer unrelated questions or use tools for other purposes."
)

logger.info("--- 🔧 Loading MCP tools from MCP Server... ---")
logger.info("--- 🤖 Creating ADK calculation Agent... ---")

root_agent = Agent(
    name="power_calculation_agent",
    model="gemini-2.5-flash",
    description="An agent that can help with power calculation conversions",
    instruction=SYSTEM_INSTRUCTION,
    tools=[
        MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=os.getenv("MCP_SERVER_URL", "http://localhost:8080/mcp")
            )
        )
    ],
)
