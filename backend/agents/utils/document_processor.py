import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def split_document_structurally(raw_text: str) -> List[str]:
    """
    Document text ko headers (#, Section) aur paragraph breaks (\\n\\n) par clean cut karta hai.
    isse beech me koi bhi sentence ya key value pair break nahi hota.
    """
    if not raw_text or not raw_text.strip():
        return []

    # Headers and section markers dhyan me rakhne ka pattern
    header_pattern = r'(?m)^(?:#{1,4}\s+.*|Section\s+\d+:?.*|SECTION\s+\d+:?.*|Part\s+\d+:?.*|PART\s+\d+:?.*)'
    
    matches = list(re.finditer(header_pattern, raw_text))
    chunks = []
    
    if len(matches) > 1:
        # Document me headers milne par section by section slice banayein
        for i in range(len(matches)):   
            start = matches[i].start()
            end = matches[i+1].start() if i + 1 < len(matches) else len(raw_text)
            chunk = raw_text[start:end].strip()
            if chunk:
                chunks.append(chunk)
    else:
        # Headers na hone par double line breaks (\\n\\n) se paragraphs alag honge
        paragraphs = [p.strip() for p in re.split(r'\n\s*\n', raw_text) if p.strip()]
        chunks = paragraphs if paragraphs else [raw_text.strip()]

    return chunks


def process_document_structurally(raw_text: str) -> Dict[str, Any]:
    """
    Main function: Plain text leta hai aur clean structural chunks ka dictionary return karta hai.
    """
    chunks = split_document_structurally(raw_text)
    
    return {
        "raw_text": raw_text,
        "structural_chunks": chunks,
        "chunk_count": len(chunks),
    }


