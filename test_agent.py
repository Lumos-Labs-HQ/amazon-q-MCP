"""Test the intelligent documentation search agent."""

import asyncio
from src import mcp


async def test_agent():
    """Test the autonomous agent."""
    print("=" * 60)
    print("Testing Intelligent Documentation Search Agent")
    print("=" * 60)
    
    tool = mcp._tool_manager._tools['search_documentation_intelligently']
    
    print("\nSearching Python asyncio docs for 'task cancellation'...")
    result = await tool.fn(
        start_url="https://docs.python.org/3/library/asyncio.html",
        problem_description="How to handle task cancellation in asyncio",
        max_pages=5
    )
    
    print(f"\n[OK] Result length: {len(result)} chars")
    print(f"\nPreview:\n{result[:500]}...")
    
    print("\n" + "=" * 60)
    print("Agent test completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_agent())
