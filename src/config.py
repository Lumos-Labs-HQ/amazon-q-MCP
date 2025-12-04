"""Configuration constants for the MCP server."""

# HTTP client configuration
HTTP_TIMEOUT = 30.0
MAX_CONTENT_LENGTH = 10000000  # 10MB max content (no practical limit for testing)
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Agent configuration
AGENT_MAX_PAGES = 10  # Maximum pages to visit during autonomous navigation
AGENT_MAX_DEPTH = 3   # Maximum navigation depth

# Elements to remove completely
REMOVE_TAGS = [
    'script', 'style', 'nav', 'footer', 'header', 'aside',
    'noscript', 'iframe', 'svg', 'canvas', 'video', 'audio',
    'form', 'button', 'input', 'select', 'textarea',
    'advertisement', 'ads', 'cookie-banner', 'popup'
]

# CSS classes/IDs that typically contain non-content elements
REMOVE_PATTERNS = [
    r'nav', r'menu', r'sidebar', r'footer', r'header', r'cookie',
    r'advertisement', r'ads', r'social', r'share', r'comment',
    r'related', r'recommend', r'popup', r'modal', r'banner'
]

# Common documentation content containers
CONTENT_SELECTORS = [
    'article', 'main', '.content', '.documentation', '.doc-content',
    '.markdown-body', '.post-content', '.entry-content', '.article-content',
    '#content', '#main-content', '#documentation', '.prose',
    '[role="main"]', '[role="article"]'
]
