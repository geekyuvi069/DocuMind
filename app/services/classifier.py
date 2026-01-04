"""
Document classification service using rule-based approach.
"""
from typing import Literal


DocumentType = Literal["invoice", "resume", "legal", "unknown"]


def classify_document(text: str) -> DocumentType:
    """
    Classify document type based on keywords and patterns.
    
    Args:
        text: Raw text extracted from PDF
        
    Returns:
        Document type: invoice, resume, legal, or unknown
    """
    text_lower = text.lower()
    
    # Invoice keywords
    invoice_keywords = [
        'invoice', 'invoice number', 'invoice no', 'bill to', 'ship to',
        'total amount', 'amount due', 'due date', 'payment terms',
        'gst', 'tax', 'subtotal', 'grand total', 'vendor', 'supplier'
    ]
    invoice_score = sum(1 for keyword in invoice_keywords if keyword in text_lower)
    
    # Resume keywords
    resume_keywords = [
        'resume', 'curriculum vitae', 'cv', 'objective', 'summary',
        'experience', 'education', 'skills', 'qualifications',
        'employment history', 'work experience', 'professional experience',
        'projects', 'certifications', 'references'
    ]
    resume_score = sum(1 for keyword in resume_keywords if keyword in text_lower)
    
    # Legal keywords
    legal_keywords = [
        'legal notice', 'legal document', 'court', 'judgment', 'order',
        'section', 'subsection', 'act', 'statute', 'regulation',
        'complaint', 'petition', 'affidavit', 'warrant', 'subpoena',
        'law', 'legal', 'attorney', 'counsel', 'plaintiff', 'defendant'
    ]
    legal_score = sum(1 for keyword in legal_keywords if keyword in text_lower)
    
    # Determine document type based on highest score
    scores = {
        'invoice': invoice_score,
        'resume': resume_score,
        'legal': legal_score
    }
    
    max_score = max(scores.values())
    
    if max_score == 0:
        return "unknown"
    
    # Return the type with highest score
    for doc_type, score in scores.items():
        if score == max_score:
            return doc_type
    
    return "unknown"

