"""
Amazon Q Web Documentation Reader - Source Package

This package contains the MCP server implementation for reading
web documentation and extracting content for Amazon Q.
"""

from .server import mcp
from . import tools  # Import to register tools

__all__ = ["mcp"]
