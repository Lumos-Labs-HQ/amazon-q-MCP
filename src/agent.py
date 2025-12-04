"""Autonomous documentation navigation agent."""

import re
from urllib.parse import urlparse

from .fetcher import fetch_url
from .extractor import DocumentExtractor


class DocAgent:
    """Autonomous agent for navigating and extracting documentation."""
    
    def __init__(self, max_pages: int = 10, max_depth: int = 3):
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.visited = set()
        self.collected = []
    
    def _get_keywords(self, problem: str) -> list[str]:
        """Extract keywords from problem description."""
        words = re.findall(r'\b\w{3,}\b', problem.lower())
        stopwords = {'the', 'and', 'for', 'with', 'this', 'that', 'have', 'from', 'are', 'was', 'were'}
        return [w for w in words if w not in stopwords]
    
    def _score_relevance(self, text: str, url: str, keywords: list[str]) -> float:
        """Calculate relevance score."""
        text_lower = text.lower()
        url_lower = url.lower()
        
        score = sum(2.0 for kw in keywords if kw in text_lower)
        score += sum(1.5 for kw in keywords if kw in url_lower)
        
        # Boost doc indicators
        if any(ind in text_lower or ind in url_lower for ind in ['api', 'guide', 'tutorial', 'reference', 'example']):
            score += 0.5
        
        return score
    
    def _filter_links(self, links: list[dict], base_domain: str, keywords: list[str]) -> list[dict]:
        """Filter and rank links by relevance."""
        relevant = []
        
        for link in links:
            url = link['url']
            
            # Same domain only
            if urlparse(url).netloc != base_domain:
                continue
            
            # Skip visited
            if url in self.visited:
                continue
            
            # Skip non-doc URLs
            if any(skip in url.lower() for skip in ['login', 'signup', 'download', 'pricing', 'blog']):
                continue
            
            score = self._score_relevance(link['text'], url, keywords)
            if score > 0:
                relevant.append({**link, 'score': score})
        
        relevant.sort(key=lambda x: x['score'], reverse=True)
        return relevant[:5]
    
    async def _explore(self, url: str, keywords: list[str], depth: int) -> None:
        """Recursively explore pages."""
        if depth > self.max_depth or len(self.visited) >= self.max_pages or url in self.visited:
            return
        
        self.visited.add(url)
        
        try:
            html, final_url = await fetch_url(url)
            extractor = DocumentExtractor(html, final_url)
            data = extractor.extract_as_markdown()
            
            # Check content relevance
            relevance = sum(1 for kw in keywords if kw in data['content'].lower())
            
            if relevance > 0:
                self.collected.append({
                    'url': final_url,
                    'title': data['title'],
                    'content': data['content'],
                    'relevance': relevance
                })
            
            # Explore further
            if depth < self.max_depth and len(self.visited) < self.max_pages:
                links = extractor.extract_links()
                base_domain = urlparse(final_url).netloc
                relevant_links = self._filter_links(links, base_domain, keywords)
                
                for link in relevant_links:
                    if len(self.visited) >= self.max_pages:
                        break
                    await self._explore(link['url'], keywords, depth + 1)
        
        except Exception:
            pass
    
    async def search(self, start_url: str, problem: str) -> dict:
        """Search documentation for problem-relevant information."""
        self.visited.clear()
        self.collected.clear()
        
        keywords = self._get_keywords(problem)
        await self._explore(start_url, keywords, 0)
        
        self.collected.sort(key=lambda x: x['relevance'], reverse=True)
        
        return {
            'problem': problem,
            'start_url': start_url,
            'pages_visited': len(self.visited),
            'relevant_pages': len(self.collected),
            'content': self.collected
        }
