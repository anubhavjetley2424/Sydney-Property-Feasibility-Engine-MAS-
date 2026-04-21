import os
from langchain_mcp_adapters.tools import load_mcp_tools

try:
    tools = load_mcp_tools("uvx", ["excel-mcp-server", "stdio"])
    print(f"Excel MCP tools loaded: {len(tools)}")
    for t in tools:
        print(getattr(t, "name", t))
except Exception as e:
    print(f"Excel MCP test failed: {e}")
