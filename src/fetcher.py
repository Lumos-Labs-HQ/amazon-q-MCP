"""HTTP fetching utilities."""

import httpx
from .config import HTTP_TIMEOUT, MAX_CONTENT_LENGTH, USER_AGENT


async def fetch_url(url: str) -> tuple[str, str]:
    """
    Fetch content from a URL.
    
    Args:
        url: The URL to fetch
        
    Returns:
        Tuple of (content, final_url) after any redirects
        
    Raises:
        httpx.HTTPStatusError: If HTTP request fails
        httpx.RequestError: If connection fails
        ValueError: If content is too large
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
