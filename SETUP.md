# Quick Setup Guide

## 1. Install Dependencies

```bash
cd amazon-q-web_search
uv sync
```

## 2. Add to Amazon Q

Create `~/.aws/amazonq/mcp.json`:

```bash
mkdir -p ~/.aws/amazonq
```

**Linux/WSL:**
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

**macOS:**
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

**Windows:**
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

## 3. Verify

```bash
q chat
```

Then type:
```
/mcp
```

You should see `doc_reader` with 5 tools!

## 4. Test

Ask Amazon Q:
```
I'm having issues with Razorpay routes.
Documentation: https://razorpay.com/docs/
```

Watch Amazon Q navigate the docs intelligently! 🚀
