"""
Document data models.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class Document(BaseModel):
    """Document model for MongoDB storage."""
    
    id: Optional[str] = Field(None, alias="_id")
    filename: str
    file_path: str
    document_type: str  # invoice, resume, legal, unknown
    raw_text: str
    extracted_fields: Dict[str, Any] = {}
    uploaded_by: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "processed"  # processed, failed
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "filename": "invoice_001.pdf",
                "file_path": "uploads/invoice_001.pdf",
                "document_type": "invoice",
                "raw_text": "Invoice content...",
                "extracted_fields": {
                    "invoice_no": "INV-001",
                    "vendor": "ABC Corp",
                    "amount": 1000.00,
                    "due_date": "2024-12-31"
                },
                "uploaded_by": "admin",
                "status": "processed"
            }
        }


class DocumentCreate(BaseModel):
    """Schema for creating a document."""
    filename: str
    file_path: str
    document_type: str
    raw_text: str
    extracted_fields: Dict[str, Any] = {}
    uploaded_by: str


class DocumentResponse(BaseModel):
    """Response schema for document."""
    id: str
    filename: str
    document_type: str
    extracted_fields: Dict[str, Any]
    uploaded_by: str
    uploaded_at: datetime
    status: str
    
    class Config:
        from_attributes = True

