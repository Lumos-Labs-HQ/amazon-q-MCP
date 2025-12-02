"""
Amazon Q Web Documentation Reader - MCP Server

This MCP server provides tools to fetch and extract documentation
content from web pages for use with Amazon Q.

Usage:
    Run directly: python main.py
    Or with uv: uv run main.py
"""

from src.doc_reader import mcp


def main():
    """Start the MCP server."""
    print("Starting Amazon Q Web Documentation Reader MCP Server...")
    mcp.run()


if __name__ == "__main__":
    main()
