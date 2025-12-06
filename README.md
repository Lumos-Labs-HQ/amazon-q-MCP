<div align="center">

# 🌐 Amazon Q Web Documentation Reader

### MCP Server for Intelligent Web Content Extraction

[![Python](https://img.shields.io/badge/Python-3.12+-3776ab?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![MCP](https://img.shields.io/badge/MCP-Compatible-00d4aa?style=for-the-badge&logo=amazon&logoColor=white)](https://modelcontextprotocol.io)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

<p align="center">
  <strong>A Model Context Protocol (MCP) server that enables Amazon Q to intelligently navigate and extract documentation from websites.</strong>
  <br>
  <em>Amazon Q uses Claude 4.5 to make smart decisions about which pages to visit and what content to extract.</em>
</p>

[Features](#-features) •
[Installation](#-installation) •
[Setup](#-setup-with-amazon-q) •
[Usage](#-usage) •
[Tools](#-available-tools)

</div>

---

## ✨ Features

- 🧠 **Intelligent Navigation** - Amazon Q (Claude 4.5) decides which documentation pages to visit
- 🧹 **Clean Content Extraction** - Removes navigation, ads, scripts, and other non-content elements
- 📝 **Multiple Output Formats** - Supports both Markdown and plain text output
- 💻 **Code Block Extraction** - Specifically extracts code examples from documentation
- 📊 **Page Structure Analysis** - Extracts heading hierarchy and table of contents
- 🔗 **Link Discovery** - Finds and filters documentation links
- 📚 **Batch Processing** - Read multiple documentation pages at once

---

## 🎯 How It Works

```
User: "I'm having issues with Razorpay routes"
      Documentation: https://razorpay.com/docs

Amazon Q (Claude 4.5):
  1. Reads main docs page
  2. Sees links: ["Payments", "Routes", "Webhooks", ...]
  3. Intelligently decides: "Routes link is relevant!"
  4. Navigates to Routes documentation
  5. Extracts content and solves your problem

All navigation decisions = Amazon Q's Claude brain 🧠
MCP Server = Clean content extraction tool 🛠️
```

---

## 📦 Installation

### Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- [Amazon Q CLI](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/command-line-installing.html)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/amazon-q-web_search.git
cd amazon-q-web_search
```

### Step 2: Install Dependencies

**Using uv (Recommended):**
```bash
uv sync
```

**Using pip:**
```bash
pip install -e .
```

---

## 🔧 Setup with Amazon Q

### Step 1: Locate Your MCP Configuration File

Amazon Q looks for MCP server configuration in:
- **Linux/WSL**: `~/.aws/amazonq/mcp.json`
- **macOS**: `~/.aws/amazonq/mcp.json`
- **Windows**: `%USERPROFILE%\.aws\amazonq\mcp.json`

### Step 2: Create/Edit the Configuration File

Create the directory if it doesn't exist:
```bash
mkdir -p ~/.aws/amazonq
```

Edit or create `~/.aws/amazonq/mcp.json`:

**For Linux/WSL:**
```json
{
  "mcpServers": {
    "doc_reader": {
      "command": "/full/path/to/amazon-q-web_search/.venv/bin/python",
      "args": ["/full/path/to/amazon-q-web_search/main.py"]
    }
  }
}
```

**For macOS:**
```json
{
  "mcpServers": {
    "doc_reader": {
      "command": "/full/path/to/amazon-q-web_search/.venv/bin/python",
      "args": ["/full/path/to/amazon-q-web_search/main.py"]
    }
  }
}
```

**For Windows:**
```json
{
  "mcpServers": {
    "doc_reader": {
      "command": "C:\\full\\path\\to\\amazon-q-web_search\\.venv\\Scripts\\python.exe",
      "args": ["C:\\full\\path\\to\\amazon-q-web_search\\main.py"]
    }
  }
}
```

**💡 Tip:** Replace `/full/path/to/` with the actual path where you cloned the repository.

### Step 3: Verify Installation

1. **Start Amazon Q CLI:**
   ```bash
   q chat
   ```

2. **Check if MCP server is loaded:**
   ```
   /mcp
   ```

   You should see:
   ```
   doc_reader
     - read_web_documentation
     - get_documentation_links
     - get_page_structure
     - extract_code_examples
     - read_multiple_docs
   ```

3. **If not loaded:**
   - Check the file path in `mcp.json` is correct
   - Restart Amazon Q CLI
   - Check logs: `q chat logdump`

---

## 🚀 Usage

### Basic Example

In Amazon Q CLI, simply ask about documentation:

```
I'm having issues with Razorpay routes. Can you help me understand how they work?
Documentation: https://razorpay.com/docs/
```

Amazon Q will:
1. ✅ Read the main documentation page
2. ✅ Extract all available links
3. ✅ Intelligently identify the "Routes" link
4. ✅ Navigate to the Routes documentation
5. ✅ Provide you with accurate information

### More Examples

**Python Documentation:**
```
Can you explain Python asyncio event loops?
Documentation: https://docs.python.org/3/library/asyncio.html
```

**FastAPI Tutorial:**
```
How do I create a basic FastAPI application?
Documentation: https://fastapi.tiangolo.com/
```

**AWS Lambda:**
```
How do I create a Lambda function with Python?
Documentation: https://docs.aws.amazon.com/lambda/
```

---

## 🛠 Available Tools

Amazon Q intelligently chains these tools to navigate documentation:

### 1. `read_web_documentation`
Fetches and extracts clean documentation content from a web page.

**Parameters:**
- `url` (required): The URL of the documentation page
- `output_format` (optional): `"markdown"` (default) or `"text"`

**Returns:** Extracted documentation content with title and metadata

---

### 2. `get_documentation_links`
Extracts all links from a documentation page with optional filtering.

**Parameters:**
- `url` (required): The URL of the documentation page
- `filter_pattern` (optional): Pattern to filter links (e.g., `"api"`, `"guide"`)

**Returns:** List of links found on the page

---

### 3. `get_page_structure`
Extracts the heading structure and table of contents from a documentation page.

**Parameters:**
- `url` (required): The URL of the documentation page

**Returns:** Hierarchical structure of headings on the page

---

### 4. `extract_code_examples`
Extracts all code blocks from a documentation page.

**Parameters:**
- `url` (required): The URL of the documentation page

**Returns:** All code blocks found with their detected languages

---

### 5. `read_multiple_docs`
Reads multiple documentation pages and combines their content.

**Parameters:**
- `urls` (required): List of documentation URLs (max 10)

**Returns:** Combined content from all pages

---

## 📁 Project Structure

```
amazon-q-web_search/
├── main.py              # Entry point
├── pyproject.toml       # Project configuration
├── README.md            # This file
├── run_mcp.sh           # Startup script (Linux/macOS)
└── src/
    ├── __init__.py      # Package initialization
    ├── server.py        # MCP server initialization
    ├── config.py        # Configuration constants
    ├── fetcher.py       # HTTP fetching logic
    ├── extractor.py     # HTML content extraction
    ├── formatters.py    # Output formatting
    └── tools.py         # MCP tool definitions
```

---

## ⚙️ Configuration

Edit `src/config.py` to customize behavior:

| Setting | Default | Description |
|---------|---------|-------------|
| `HTTP_TIMEOUT` | 30.0s | Request timeout in seconds |
| `MAX_CONTENT_LENGTH` | 10MB | Maximum content size in bytes |
| `USER_AGENT` | Custom | HTTP User-Agent string |
| `REMOVE_TAGS` | Various | HTML tags to remove during extraction |
| `CONTENT_SELECTORS` | Various | Selectors for finding main content |

---

## 🐛 Troubleshooting

### MCP Server Not Loading

**Check configuration:**
```bash
cat ~/.aws/amazonq/mcp.json
```

**Verify paths are correct:**
- Use absolute paths, not relative
- Check that Python executable exists
- Check that main.py exists

**Test server manually:**
```bash
cd /path/to/amazon-q-web_search
.venv/bin/python main.py
```

**Check Amazon Q logs:**
```bash
q chat logdump
```

### Server Starts But Tools Don't Work

**Verify dependencies are installed:**
```bash
cd /path/to/amazon-q-web_search
.venv/bin/python -c "import httpx, bs4, markdownify; print('OK')"
```

**Reinstall dependencies:**
```bash
uv sync --reinstall
```

### Connection Timeout

**Increase timeout in settings:**
```bash
q settings mcp.initTimeout 60000
```

---

## 📚 Dependencies

| Package | Purpose |
|---------|---------|
| [httpx](https://www.python-httpx.org/) | Async HTTP client for fetching web pages |
| [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/) | HTML parsing and navigation |
| [lxml](https://lxml.de/) | Fast XML/HTML parser |
| [markdownify](https://github.com/matthewwithanm/python-markdownify) | HTML to Markdown conversion |
| [mcp](https://modelcontextprotocol.io/) | Model Context Protocol SDK |

---

## ⚠️ Limitations

| Limit | Value |
|-------|-------|
| Maximum content size | 10MB per page |
| Maximum URLs per batch | 10 |
| Request timeout | 30 seconds |
| Content type | HTML only |

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 💬 Support

- 📫 Open an [Issue](https://github.com/yourusername/amazon-q-web_search/issues) for bug reports or feature requests
- ⭐ Star this repo if you find it useful!

---

<div align="center">
  <sub>Built with ❤️ for Amazon Q Developer</sub>
</div>
