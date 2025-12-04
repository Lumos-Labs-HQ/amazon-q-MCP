"""Output formatting utilities."""

from typing import Any


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


def format_agent_results(results: dict[str, Any]) -> str:
    """Format autonomous agent search results."""
    output = []
    
    output.append(f"# Intelligent Documentation Search Results\n")
    output.append(f"**Problem:** {results['problem']}\n")
    output.append(f"**Starting URL:** {results['start_url']}\n")
    output.append(f"**Pages Visited:** {results['pages_visited']}")
    output.append(f"**Relevant Pages Found:** {results['relevant_pages']}\n")
    output.append("---\n")
    
    if not results['content']:
        output.append("No relevant documentation found for this problem.\n")
        return '\n'.join(output)
    
    for i, page in enumerate(results['content'], 1):
        output.append(f"## {i}. {page['title']}\n")
        output.append(f"**URL:** {page['url']}")
        output.append(f"**Relevance Score:** {page['relevance']}\n")
        output.append(page['content'])
        output.append("\n---\n")
    
    return '\n'.join(output)
