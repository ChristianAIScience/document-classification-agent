import json
import sqlite3
import asyncio
import logging
import os
from typing import Annotated

from fastmcp import FastMCP

logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

mcp = FastMCP(name="SQL TEST MCP Server 💵", json_response=True)

DB_PATH = "pv_demo.db"


@mcp.tool
async def get_sum_of_pv_power_data(
    date: Annotated[str, "Date in format YYYY-MM-DD"]):
    """
    Get the sum of DC power data for a specific date from the database.
    """

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    query = """
        SELECT *
        FROM pv_power
        WHERE Date = ?
    """

    cursor.execute(query, (date,))

    rows = cursor.fetchall()

    if not rows:
        return "No data found"
    
    total = sum(row["DC_Power_W_PV1"] for row in rows)

    cursor.close()
    conn.close()

    result = {
        "date": date,
        "total_dc_power_w_pv1": total
        }
    return json.dumps(result, indent=2, default=str)


if __name__ == "__main__":
    logger.info(f"🚀 MCP server started on port {os.getenv('PORT', 8080)}")
    asyncio.run(
        mcp.run_async(transport="http",
                      host="0.0.0.0",
                      port=os.getenv("PORT", 8080))
                      )
    