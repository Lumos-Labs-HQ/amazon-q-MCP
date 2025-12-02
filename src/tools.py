"""MCP tool definitions for web documentation reading."""

from urllib.parse import urlparse
import re

import httpx

from .server import mcp
from .fetcher import fetch_url
from .extractor import DocumentExtractor
from .formatters import format_output


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
