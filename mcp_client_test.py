
import asyncio, sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    params = StdioServerParameters(command=sys.executable, args=["mcp_server.py"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("TOOLS:", [t.name for t in tools.tools])
            r = await session.call_tool("search_assets",
                                        {"criticality": "High"})
            print("HIGH-CRIT:", r.content[0].text[:300], "...")
            await session.call_tool("remember",
                {"key": "day2", "note": "custom MCP server works"})
            r = await session.call_tool("recall", {})
            print("MEMORY:", r.content[0].text)

asyncio.run(main())
