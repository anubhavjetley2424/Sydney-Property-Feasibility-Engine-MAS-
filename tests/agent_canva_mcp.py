from langchain_mcp_adapters.tools import load_mcp_tools

try:
    tools = load_mcp_tools("npx", ["@canva/cli@latest", "mcp", "stdio"])
    print(f"Canva MCP tools loaded: {len(tools)}")
    for t in tools:
        print(getattr(t, "name", t))
except Exception as e:
    print(f"Canva MCP test failed: {e}")
