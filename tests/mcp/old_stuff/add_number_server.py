
from fastmcp import FastMCP

mcp = FastMCP("Mein Test Server")


@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """Addiert zwei Zahlen."""
    return a + b


if __name__ == "__main__":
    # WICHTIG: transport="http" und Port festlegen
    # FastMCP nutzt standardmäßig Port 8000 oder 8080
    mcp.run(transport="http", host="0.0.0.0", port=8001)

