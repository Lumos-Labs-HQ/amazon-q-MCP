"""
MCP Server for Amazon Q - Web Documentation Reader

This module provides tools to fetch and extract documentation content
from web pages, making it available for Amazon Q to use.
"""

from typing import Any
from urllib.parse import urljoin, urlparse
import re

import httpx
from bs4 import BeautifulSoup, NavigableString, Tag
from markdownify import markdownify as md
from mcp.server.fastmcp import FastMCP

# Initialize MCP Server
mcp = FastMCP(
    "doc_reader",
    description="Web Documentation Reader for Amazon Q - Fetches and extracts clean documentation content from websites"
)

# HTTP client configuration
HTTP_TIMEOUT = 30.0
MAX_CONTENT_LENGTH = 500000  # 500KB max content
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


class DocumentExtractor:
    """Extracts clean documentation content from HTML pages."""
    
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
    
    def __init__(self, html: str, base_url: str):
        self.soup = BeautifulSoup(html, 'lxml')
        self.base_url = base_url
        
    def _remove_unwanted_elements(self) -> None:
        """Remove scripts, styles, navigation, and other non-content elements."""
        # Remove by tag name
        for tag in self.REMOVE_TAGS:
            for element in self.soup.find_all(tag):
                element.decompose()
        
        # Remove by class/id patterns
        pattern = re.compile('|'.join(self.REMOVE_PATTERNS), re.IGNORECASE)
        for element in self.soup.find_all(True):
            classes = ' '.join(element.get('class', []))
            element_id = element.get('id', '')
            if pattern.search(classes) or pattern.search(element_id):
                # Don't remove if it's a main content container
                if not any(element.find_all(class_=re.compile(r'content|article|main', re.I))):
                    element.decompose()
    
    def _find_main_content(self) -> Tag | None:
        """Find the main content container of the page."""
        for selector in self.CONTENT_SELECTORS:
            try:
                if selector.startswith('.'):
                    content = self.soup.find(class_=selector[1:])
                elif selector.startswith('#'):
                    content = self.soup.find(id=selector[1:])
                elif selector.startswith('['):
                    # Handle attribute selectors
                    match = re.match(r'\[(\w+)="([^"]+)"\]', selector)
                    if match:
                        content = self.soup.find(attrs={match.group(1): match.group(2)})
                    else:
                        content = None
                else:
                    content = self.soup.find(selector)
                
                if content and len(content.get_text(strip=True)) > 100:
                    return content
            except Exception:
                continue
        
        # Fallback to body
        return self.soup.find('body')
    
    def _extract_title(self) -> str:
        """Extract the page title."""
        # Try h1 first
        h1 = self.soup.find('h1')
        if h1:
            return h1.get_text(strip=True)
        
        # Try title tag
        title = self.soup.find('title')
        if title:
            return title.get_text(strip=True)
        
        return "Untitled Document"
    
    def _extract_description(self) -> str:
        """Extract page description from meta tags."""
        meta_desc = self.soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content']
        
        og_desc = self.soup.find('meta', attrs={'property': 'og:description'})
        if og_desc and og_desc.get('content'):
            return og_desc['content']
        
        return ""
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r' +\n', '\n', text)
        text = re.sub(r'\n +', '\n', text)
        return text.strip()
    
    def extract_as_text(self) -> dict[str, Any]:
        """Extract documentation as plain text."""
        self._remove_unwanted_elements()
        
        title = self._extract_title()
        description = self._extract_description()
        
        content_element = self._find_main_content()
        
        if content_element:
            content = content_element.get_text(separator='\n', strip=True)
        else:
            content = self.soup.get_text(separator='\n', strip=True)
        
        content = self._clean_text(content)
        
        return {
            "title": title,
            "description": description,
            "content": content,
            "url": self.base_url,
            "format": "text"
        }
    
    def extract_as_markdown(self) -> dict[str, Any]:
        """Extract documentation as Markdown."""
        self._remove_unwanted_elements()
        
        title = self._extract_title()
        description = self._extract_description()
        
        content_element = self._find_main_content()
        
        if content_element:
            # Convert to markdown
            content = md(str(content_element), heading_style="ATX", bullets="-")
        else:
            body = self.soup.find('body')
            if body:
                content = md(str(body), heading_style="ATX", bullets="-")
            else:
                content = md(str(self.soup), heading_style="ATX", bullets="-")
        
        content = self._clean_text(content)
        
        return {
            "title": title,
            "description": description,
            "content": content,
            "url": self.base_url,
            "format": "markdown"
        }
    
    def extract_code_blocks(self) -> list[dict[str, str]]:
        """Extract all code blocks from the page."""
        code_blocks = []
        
        # Find pre > code blocks
        for pre in self.soup.find_all('pre'):
            code = pre.find('code')
            if code:
                language = ""
                classes = code.get('class', [])
                for cls in classes:
                    if cls.startswith('language-') or cls.startswith('lang-'):
                        language = cls.split('-', 1)[1]
                        break
                    elif cls in ['python', 'javascript', 'java', 'typescript', 'bash', 'shell', 'json', 'yaml', 'html', 'css']:
                        language = cls
                        break
                
                code_blocks.append({
                    "language": language,
                    "code": code.get_text(strip=True)
                })
            else:
                code_blocks.append({
                    "language": "",
                    "code": pre.get_text(strip=True)
                })
        
        return code_blocks
    
    def extract_headings(self) -> list[dict[str, Any]]:
        """Extract heading structure from the page."""
        headings = []
        
        for level in range(1, 7):
            for heading in self.soup.find_all(f'h{level}'):
                headings.append({
                    "level": level,
                    "text": heading.get_text(strip=True)
                })
        
        return headings
    
    def extract_links(self) -> list[dict[str, str]]:
        """Extract all links from the page."""
        links = []
        
        for a in self.soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text(strip=True)
            
            # Convert relative URLs to absolute
            if href and not href.startswith(('http://', 'https://', 'mailto:', 'tel:', '#', 'javascript:')):
                href = urljoin(self.base_url, href)
            
            if href and text and href.startswith(('http://', 'https://')):
                links.append({
                    "text": text,
                    "url": href
                })
        
        return links


async def fetch_url(url: str) -> tuple[str, str]:
    """
    Fetch content from a URL.
    
    Returns:
        Tuple of (content, final_url) after any redirects
    """
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    
    async with httpx.AsyncClient(follow_redirects=True, timeout=HTTP_TIMEOUT) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        
        # Check content length
        content_length = len(response.content)
        if content_length > MAX_CONTENT_LENGTH:
            raise ValueError(f"Content too large: {content_length} bytes (max: {MAX_CONTENT_LENGTH})")
        
        return response.text, str(response.url)


def format_output(data: dict[str, Any], include_metadata: bool = True) -> str:
    """Format extracted data for Amazon Q consumption."""
    output_parts = []
    
    if include_metadata:
        output_parts.append(f"# {data['title']}")
        output_parts.append(f"\n**Source:** {data['url']}")
        
        if data.get('description'):
            output_parts.append(f"\n**Description:** {data['description']}")
        
        output_parts.append(f"\n**Format:** {data['format']}")
        output_parts.append("\n---\n")
    
    output_parts.append(data['content'])
    
    return '\n'.join(output_parts)


# ============================================================================
# MCP TOOLS
# ============================================================================

@mcp.tool()
async def read_web_documentation(url: str, output_format: str = "markdown") -> str:
    """
    Fetches and extracts clean documentation content from a web page.
    
    This tool is designed to read documentation websites and extract the main
    content in a clean, readable format suitable for analysis.
    
    Args:
        url: The URL of the documentation page to read
        output_format: Output format - "markdown" (default) or "text"
    
    Returns:
        Extracted documentation content with title and metadata
    """
    try:
        # Validate URL
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return f"Error: Invalid URL format. Please provide a complete URL (e.g., https://example.com/docs)"
        
        # Fetch the page
        html_content, final_url = await fetch_url(url)
        
        # Extract content
        extractor = DocumentExtractor(html_content, final_url)
        
        if output_format.lower() == "text":
            data = extractor.extract_as_text()
        else:
            data = extractor.extract_as_markdown()
        
        return format_output(data)
        
    except httpx.HTTPStatusError as e:
        return f"Error: HTTP {e.response.status_code} - Failed to fetch URL: {url}"
    except httpx.RequestError as e:
        return f"Error: Failed to connect to URL: {url}. Details: {str(e)}"
    except Exception as e:
        return f"Error: Failed to process documentation. Details: {str(e)}"


@mcp.tool()
async def extract_code_examples(url: str) -> str:
    """
    Extracts all code examples/blocks from a documentation page.
    
    This tool specifically targets code blocks in documentation, useful for
    finding implementation examples, snippets, and code samples.
    
    Args:
        url: The URL of the documentation page
    
    Returns:
        All code blocks found on the page with their detected languages
    """
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return f"Error: Invalid URL format. Please provide a complete URL"
        
        html_content, final_url = await fetch_url(url)
        extractor = DocumentExtractor(html_content, final_url)
        
        code_blocks = extractor.extract_code_blocks()
        
        if not code_blocks:
            return f"No code blocks found on: {url}"
        
        output_parts = [f"# Code Examples from: {url}\n"]
        output_parts.append(f"Found {len(code_blocks)} code block(s)\n")
        output_parts.append("---\n")
        
        for i, block in enumerate(code_blocks, 1):
            lang = block['language'] or 'unknown'
            output_parts.append(f"## Code Block {i} ({lang})\n")
            output_parts.append(f"```{block['language']}\n{block['code']}\n```\n")
        
        return '\n'.join(output_parts)
        
    except httpx.HTTPStatusError as e:
        return f"Error: HTTP {e.response.status_code} - Failed to fetch URL: {url}"
    except httpx.RequestError as e:
        return f"Error: Failed to connect to URL: {url}. Details: {str(e)}"
    except Exception as e:
        return f"Error: Failed to extract code examples. Details: {str(e)}"


@mcp.tool()
async def get_page_structure(url: str) -> str:
    """
    Extracts the heading structure and table of contents from a documentation page.
    
    This tool helps understand the organization of a documentation page by
    extracting all headings and their hierarchy.
    
    Args:
        url: The URL of the documentation page
    
    Returns:
        Hierarchical structure of headings on the page
    """
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return f"Error: Invalid URL format. Please provide a complete URL"
        
        html_content, final_url = await fetch_url(url)
        extractor = DocumentExtractor(html_content, final_url)
        
        # Get title and description
        title = extractor._extract_title()
        description = extractor._extract_description()
        
        # Remove unwanted elements first
        extractor._remove_unwanted_elements()
        headings = extractor.extract_headings()
        
        if not headings:
            return f"No headings found on: {url}"
        
        output_parts = [f"# Page Structure: {title}\n"]
        output_parts.append(f"**URL:** {url}\n")
        
        if description:
            output_parts.append(f"**Description:** {description}\n")
        
        output_parts.append("\n## Table of Contents\n")
        
        for heading in headings:
            indent = "  " * (heading['level'] - 1)
            output_parts.append(f"{indent}- {heading['text']}")
        
        return '\n'.join(output_parts)
        
    except httpx.HTTPStatusError as e:
        return f"Error: HTTP {e.response.status_code} - Failed to fetch URL: {url}"
    except httpx.RequestError as e:
        return f"Error: Failed to connect to URL: {url}. Details: {str(e)}"
    except Exception as e:
        return f"Error: Failed to get page structure. Details: {str(e)}"


@mcp.tool()
async def get_documentation_links(url: str, filter_pattern: str = "") -> str:
    """
    Extracts all links from a documentation page, useful for discovering related docs.
    
    This tool helps navigate documentation by finding all links on a page,
    optionally filtering by a pattern.
    
    Args:
        url: The URL of the documentation page
        filter_pattern: Optional pattern to filter links (e.g., "api", "guide")
    
    Returns:
        List of links found on the page
    """
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return f"Error: Invalid URL format. Please provide a complete URL"
        
        html_content, final_url = await fetch_url(url)
        extractor = DocumentExtractor(html_content, final_url)
        
        links = extractor.extract_links()
        
        # Filter if pattern provided
        if filter_pattern:
            pattern = re.compile(filter_pattern, re.IGNORECASE)
            links = [l for l in links if pattern.search(l['text']) or pattern.search(l['url'])]
        
        if not links:
            filter_msg = f" matching '{filter_pattern}'" if filter_pattern else ""
            return f"No links found{filter_msg} on: {url}"
        
        # Remove duplicates while preserving order
        seen = set()
        unique_links = []
        for link in links:
            if link['url'] not in seen:
                seen.add(link['url'])
                unique_links.append(link)
        
        output_parts = [f"# Links from: {url}\n"]
        
        if filter_pattern:
            output_parts.append(f"**Filter:** {filter_pattern}\n")
        
        output_parts.append(f"Found {len(unique_links)} unique link(s)\n")
        output_parts.append("---\n")
        
        for link in unique_links:
            output_parts.append(f"- [{link['text']}]({link['url']})")
        
        return '\n'.join(output_parts)
        
    except httpx.HTTPStatusError as e:
        return f"Error: HTTP {e.response.status_code} - Failed to fetch URL: {url}"
    except httpx.RequestError as e:
        return f"Error: Failed to connect to URL: {url}. Details: {str(e)}"
    except Exception as e:
        return f"Error: Failed to get documentation links. Details: {str(e)}"


@mcp.tool()
async def read_multiple_docs(urls: list[str]) -> str:
    """
    Reads multiple documentation pages and combines their content.
    
    This tool fetches and extracts content from multiple URLs, useful when
    documentation is spread across several pages.
    
    Args:
        urls: List of documentation URLs to read
    
    Returns:
        Combined content from all pages
    """
    if not urls:
        return "Error: No URLs provided"
    
    if len(urls) > 10:
        return "Error: Maximum 10 URLs allowed per request"
    
    results = []
    
    for url in urls:
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                results.append(f"## Error: {url}\nInvalid URL format\n")
                continue
            
            html_content, final_url = await fetch_url(url)
            extractor = DocumentExtractor(html_content, final_url)
            data = extractor.extract_as_markdown()
            
            results.append(f"## {data['title']}\n")
            results.append(f"**Source:** {data['url']}\n")
            if data.get('description'):
                results.append(f"**Description:** {data['description']}\n")
            results.append("\n" + data['content'] + "\n")
            results.append("\n---\n")
            
        except httpx.HTTPStatusError as e:
            results.append(f"## Error: {url}\nHTTP {e.response.status_code}\n")
        except httpx.RequestError as e:
            results.append(f"## Error: {url}\nConnection failed: {str(e)}\n")
        except Exception as e:
            results.append(f"## Error: {url}\nProcessing failed: {str(e)}\n")
    
    output = f"# Documentation from {len(urls)} page(s)\n\n"
    output += '\n'.join(results)
    
    return output