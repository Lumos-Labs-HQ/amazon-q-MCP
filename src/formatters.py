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
