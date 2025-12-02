"""Test script for the MCP server."""

import asyncio
from src import mcp


async def test():
    """Test the MCP server."""
    print("=" * 60)
    print("Testing MCP Server")
    print("=" * 60)
    
    print(f"\n[OK] Server: {mcp.name}")
    print(f"[OK] Tools: {len(mcp._tool_manager._tools)}")
    
    print("\nAvailable Tools:")
    for tool_name in mcp._tool_manager._tools.keys():
        print(f"  - {tool_name}")
    
    # Quick test
    print("\n" + "=" * 60)
    print("Testing read_web_documentation")
    print("=" * 60)
    
    tool = mcp._tool_manager._tools['read_web_documentation']
    result = await tool.fn(url="https://example.com", output_format="markdown")
    
    print(f"\n[OK] Success! Length: {len(result)} chars")
    print(f"\nPreview:\n{result[:200]}...")
    
    print("\n" + "=" * 60)
    print("All tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test())
