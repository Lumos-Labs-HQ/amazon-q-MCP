"""Document content extraction from HTML."""

from typing import Any
from urllib.parse import urljoin
import re

from bs4 import BeautifulSoup, Tag
from markdownify import markdownify as md

from .config import REMOVE_TAGS, REMOVE_PATTERNS, CONTENT_SELECTORS


class DocumentExtractor:
    """Extracts clean documentation content from HTML pages."""
    
    def __init__(self, html: str, base_url: str):
        self.soup = BeautifulSoup(html, 'lxml')
        self.base_url = base_url
        
    def _remove_unwanted_elements(self) -> None:
        """Remove scripts, styles, navigation, and other non-content elements."""
        # Remove by tag name
        for tag in REMOVE_TAGS:
            for element in self.soup.find_all(tag):
                element.decompose()
        
        # Remove by class/id patterns
        pattern = re.compile('|'.join(REMOVE_PATTERNS), re.IGNORECASE)
        for element in self.soup.find_all(True):
            if not hasattr(element, 'attrs') or element.attrs is None:
                continue
            classes = ' '.join(element.get('class', []))
            element_id = element.get('id', '')
            if pattern.search(classes) or pattern.search(element_id):
                # Don't remove if it's a main content container
                if not any(element.find_all(class_=re.compile(r'content|article|main', re.I))):
                    element.decompose()
    
    def _find_main_content(self) -> Tag | None:
        """Find the main content container of the page."""
        for selector in CONTENT_SELECTORS:
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
        if meta_desc:
            content = meta_desc.get('content')
            if content:
                return content
        
        og_desc = self.soup.find('meta', attrs={'property': 'og:description'})
        if og_desc:
            content = og_desc.get('content')
            if content:
                return content
        
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
