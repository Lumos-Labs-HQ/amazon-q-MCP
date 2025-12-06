"""
Amazon Q Web Documentation Reader - Source Package

This package contains the MCP server implementation for reading
web documentation and extracting content for Amazon Q.
"""

# Only import when explicitly needed
__all__ = ["mcp"]

def __getattr__(name):
    if name == "mcp":
        from .server import mcp
        from . import tools  # Register tools
        return mcp
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
