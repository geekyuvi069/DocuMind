"""
Structured field extraction service based on document type.
"""
from typing import Dict, Any
from app.services.classifier import DocumentType
from app.schemas.invoice import extract_invoice_fields
from app.schemas.resume import extract_resume_fields


async def extract_fields_by_type(document_type: DocumentType, text: str) -> Dict[str, Any]:
    """
    Extract structured fields based on document type.
    
    Args:
        document_type: Type of document (invoice, resume, legal, unknown)
        text: Raw text extracted from PDF
        
    Returns:
        Dictionary with extracted fields
    """
    if document_type == "invoice":
        return extract_invoice_fields(text)
    elif document_type == "resume":
        return extract_resume_fields(text)
    elif document_type == "legal":
        # Legal documents - extract basic info
        return {
            "document_type": "legal",
            "has_sections": "section" in text.lower() or "subsection" in text.lower(),
            "has_dates": any(char.isdigit() for char in text[:500])
        }
    else:
        # Unknown document type
        return {
            "document_type": "unknown",
            "text_length": len(text),
            "word_count": len(text.split())
        }

