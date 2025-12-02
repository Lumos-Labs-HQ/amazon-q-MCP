# Amazon Q Web Documentation Reader - MCP Server

A Model Context Protocol (MCP) server that enables Amazon Q to read and extract content from web documentation pages.

## Features

- **Read Web Documentation**: Fetch and extract clean content from any web documentation page
- **Extract Code Examples**: Pull out all code blocks with language detection
- **Get Page Structure**: Extract heading hierarchy and table of contents
- **Discover Links**: Find and filter all links on a documentation page
- **Multi-Page Reading**: Read multiple documentation pages at once

## Installation

1. Make sure you have Python 3.12+ and `uv` installed
2. Clone this repository
3. Install dependencies:

```bash
uv sync
```

## Usage

### Running the MCP Server

```bash
uv run python main.py
```

Or using the MCP CLI:

```bash
uv run mcp run src/doc_reader.py
```

### Configuring with Amazon Q

Add the following to your Amazon Q MCP configuration:

```json
{
  "mcpServers": {
    "doc_reader": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/amazon-q-web_search", "python", "main.py"]
    }
  }
}
```

## Available Tools

### `read_web_documentation`
Fetches and extracts clean documentation content from a web page.

**Parameters:**
- `url` (required): The URL of the documentation page to read
- `output_format` (optional): "markdown" (default) or "text"

**Example:**
```
Read the documentation from https://docs.python.org/3/tutorial/index.html
```

### `extract_code_examples`
Extracts all code blocks from a documentation page.

**Parameters:**
- `url` (required): The URL of the documentation page

**Example:**
```
Extract code examples from https://fastapi.tiangolo.com/tutorial/first-steps/
```

### `get_page_structure`
Extracts the heading structure and table of contents from a page.

**Parameters:**
- `url` (required): The URL of the documentation page

**Example:**
```
Get the structure of https://docs.aws.amazon.com/bedrock/
```

### `get_documentation_links`
Extracts all links from a documentation page.

**Parameters:**
- `url` (required): The URL of the documentation page
- `filter_pattern` (optional): Pattern to filter links (e.g., "api", "guide")

**Example:**
```
Get all API-related links from https://docs.example.com/
```

### `read_multiple_docs`
Reads multiple documentation pages and combines their content.

**Parameters:**
- `urls` (required): List of documentation URLs (max 10)

**Example:**
```
Read documentation from these pages: 
- https://docs.example.com/getting-started
- https://docs.example.com/api-reference
```

## Project Structure

```
amazon-q-web_search/
├── main.py              # Entry point
├── pyproject.toml       # Project configuration
├── README.md            # This file
└── src/
    ├── __init__.py      # Package init
    └── doc_reader.py    # MCP server implementation
```

## Dependencies

- `httpx` - Async HTTP client
- `mcp[cli]` - Model Context Protocol SDK
- `beautifulsoup4` - HTML parsing
- `lxml` - XML/HTML parser
- `markdownify` - HTML to Markdown conversion

## License

MIT