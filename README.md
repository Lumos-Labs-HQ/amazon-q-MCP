# Amazon Q Web Documentation Reader - MCP Server

A Model Context Protocol (MCP) server that enables Amazon Q to read and extract documentation from websites. This tool fetches web pages, extracts clean content, and provides it in a format optimized for AI consumption.

## Features

- **Clean Content Extraction**: Removes navigation, ads, scripts, and other non-content elements
- **Multiple Output Formats**: Supports both Markdown and plain text output
- **Code Block Extraction**: Specifically extracts code examples from documentation
- **Page Structure Analysis**: Extracts heading hierarchy and table of contents
- **Link Discovery**: Finds and filters documentation links
- **Batch Processing**: Read multiple documentation pages at once

## Project Structure

```
amazon-q-web_search/
├── main.py                 # Entry point
├── pyproject.toml          # Project configuration
├── README.md               # This file
└── src/
    ├── __init__.py         # Package initialization
    ├── server.py           # MCP server initialization
    ├── config.py           # Configuration constants
    ├── fetcher.py          # HTTP fetching logic
    ├── extractor.py        # HTML content extraction
    ├── formatters.py       # Output formatting
    └── tools.py            # MCP tool definitions
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd amazon-q-web_search
```

2. Install dependencies using uv:
```bash
uv sync
```

Or using pip:
```bash
pip install -e .
```

## Usage

### Running the Server

Start the MCP server:
```bash
python main.py
```

Or with uv:
```bash
uv run main.py
```

### Configuring with Amazon Q

Add this server to your Amazon Q CLI configuration (`~/.config/amazonq/mcp.json`):

```json
{
  "mcpServers": {
    "doc_reader": {
      "command": "python",
      "args": ["/path/to/amazon-q-web_search/main.py"]
    }
  }
}
```

Or with uv:
```json
{
  "mcpServers": {
    "doc_reader": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/amazon-q-web_search", "main.py"]
    }
  }
}
```

## Available Tools

### 1. read_web_documentation

Fetches and extracts clean documentation content from a web page.

**Parameters:**
- `url` (string, required): The URL of the documentation page
- `output_format` (string, optional): Output format - "markdown" (default) or "text"

**Example:**
```
Read the documentation from https://docs.python.org/3/library/asyncio.html
```

### 2. extract_code_examples

Extracts all code blocks from a documentation page.

**Parameters:**
- `url` (string, required): The URL of the documentation page

**Example:**
```
Extract code examples from https://fastapi.tiangolo.com/tutorial/first-steps/
```

### 3. get_page_structure

Extracts the heading structure and table of contents from a documentation page.

**Parameters:**
- `url` (string, required): The URL of the documentation page

**Example:**
```
Get the structure of https://docs.aws.amazon.com/lambda/latest/dg/welcome.html
```

### 4. get_documentation_links

Extracts all links from a documentation page with optional filtering.

**Parameters:**
- `url` (string, required): The URL of the documentation page
- `filter_pattern` (string, optional): Pattern to filter links (e.g., "api", "guide")

**Example:**
```
Get all links from https://react.dev/learn containing "hooks"
```

### 5. read_multiple_docs

Reads multiple documentation pages and combines their content.

**Parameters:**
- `urls` (array of strings, required): List of documentation URLs (max 10)

**Example:**
```
Read documentation from these URLs:
- https://docs.python.org/3/library/asyncio.html
- https://docs.python.org/3/library/typing.html
```

## Configuration

Edit `src/config.py` to customize:

- `HTTP_TIMEOUT`: Request timeout in seconds (default: 30.0)
- `MAX_CONTENT_LENGTH`: Maximum content size in bytes (default: 500KB)
- `USER_AGENT`: HTTP User-Agent string
- `REMOVE_TAGS`: HTML tags to remove during extraction
- `REMOVE_PATTERNS`: CSS class/ID patterns to remove
- `CONTENT_SELECTORS`: Selectors for finding main content

## Architecture

### Module Responsibilities

- **server.py**: Initializes the FastMCP server instance
- **config.py**: Centralized configuration constants
- **fetcher.py**: Handles HTTP requests with proper headers and error handling
- **extractor.py**: Contains the `DocumentExtractor` class for parsing HTML and extracting content
- **formatters.py**: Formats extracted data for Amazon Q consumption
- **tools.py**: Defines all MCP tools and their implementations

### Content Extraction Process

1. **Fetch**: HTTP request with proper headers and timeout
2. **Parse**: BeautifulSoup parses HTML into a DOM tree
3. **Clean**: Remove scripts, styles, navigation, ads, etc.
4. **Extract**: Find main content container using common selectors
5. **Convert**: Transform to Markdown or plain text
6. **Format**: Add metadata and structure for Amazon Q

## Development

### Adding New Tools

1. Define the tool function in `src/tools.py`
2. Use the `@mcp.tool()` decorator
3. Add proper docstrings for Amazon Q to understand the tool
4. Handle errors gracefully with user-friendly messages

Example:
```python
@mcp.tool()
async def my_new_tool(url: str, param: str = "default") -> str:
    """
    Brief description of what the tool does.
    
    Args:
        url: Description of url parameter
        param: Description of optional parameter
    
    Returns:
        Description of return value
    """
    try:
        # Implementation
        return result
    except Exception as e:
        return f"Error: {str(e)}"
```

### Modifying Extraction Logic

Edit `src/extractor.py` to customize:
- Content selectors
- Cleaning rules
- Extraction methods
- Output formats

### Testing

Test the server import:
```bash
python -c "from src import mcp; print('Server:', mcp.name); print('Tools:', len(mcp._tool_manager._tools))"
```

Test a specific tool:
```bash
python -c "
from src import mcp
import asyncio

async def test():
    result = await mcp._tool_manager._tools['read_web_documentation'].fn(
        'https://example.com'
    )
    print(result[:200])

asyncio.run(test())
"
```

## Dependencies

- **httpx**: Async HTTP client for fetching web pages
- **beautifulsoup4**: HTML parsing and navigation
- **lxml**: Fast XML/HTML parser
- **markdownify**: HTML to Markdown conversion
- **mcp**: Model Context Protocol SDK

## Error Handling

The server handles various error scenarios:
- Invalid URLs
- HTTP errors (404, 500, etc.)
- Connection timeouts
- Content too large
- Parsing failures

All errors return user-friendly messages to Amazon Q.

## Limitations

- Maximum content size: 500KB per page
- Maximum URLs per batch: 10
- Request timeout: 30 seconds
- Only processes HTML content

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

## Support

[Add support information here]
