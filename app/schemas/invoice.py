"""
Invoice extraction schema and utilities.
"""
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class InvoiceSchema(BaseModel):
    """Schema for invoice field extraction."""
    
    invoice_no: Optional[str] = Field(None, description="Invoice number")
    vendor: Optional[str] = Field(None, description="Vendor/supplier name")
    amount: Optional[float] = Field(None, description="Total amount")
    due_date: Optional[str] = Field(None, description="Due date")
    date: Optional[str] = Field(None, description="Invoice date")
    tax_amount: Optional[float] = Field(None, description="Tax amount")
    currency: Optional[str] = Field(None, description="Currency code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "invoice_no": "INV-2024-001",
                "vendor": "ABC Corporation",
                "amount": 1500.00,
                "due_date": "2024-12-31",
                "date": "2024-11-01",
                "tax_amount": 150.00,
                "currency": "USD"
            }
        }


def extract_invoice_fields(text: str) -> dict:
    """
    Extract invoice fields from text using rule-based patterns.
    
    Args:
        text: Raw text extracted from PDF
        
    Returns:
        Dictionary with extracted invoice fields
    """
    text_lower = text.lower()
    lines = text.split('\n')
    
    extracted = {}
    
    # Extract invoice number
    for line in lines:
        if any(keyword in line.lower() for keyword in ['invoice no', 'invoice number', 'invoice#', 'inv no']):
            # Try to extract number after keyword
            parts = line.split()
            for i, part in enumerate(parts):
                if any(kw in part.lower() for kw in ['invoice', 'inv', 'no', 'number']):
                    if i + 1 < len(parts):
                        extracted['invoice_no'] = parts[i + 1].strip(':#')
                        break
    
    # Extract vendor (look for common patterns)
    vendor_keywords = ['vendor', 'supplier', 'from', 'bill from', 'company']
    for line in lines[:20]:  # Check first 20 lines
        line_lower = line.lower()
        if any(kw in line_lower for kw in vendor_keywords):
            # Extract text after keyword
            for kw in vendor_keywords:
                if kw in line_lower:
                    parts = line.split(kw, 1)
                    if len(parts) > 1:
                        vendor = parts[1].strip().split('\n')[0].split(',')[0].strip()
                        if vendor and len(vendor) > 2:
                            extracted['vendor'] = vendor
                            break
    
    # Extract amounts
    amount_keywords = ['total', 'amount due', 'grand total', 'invoice amount']
    for line in lines:
        line_lower = line.lower()
        for kw in amount_keywords:
            if kw in line_lower:
                # Extract numbers from line
                import re
                numbers = re.findall(r'\d+\.?\d*', line)
                if numbers:
                    try:
                        amount = float(numbers[-1])  # Usually the last number is total
                        if amount > 0:
                            extracted['amount'] = amount
                            break
                    except ValueError:
                        pass
    
    # Extract dates
    import re
    date_patterns = [
        r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # MM/DD/YYYY
        r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',    # YYYY/MM/DD
    ]
    
    dates = []
    for pattern in date_patterns:
        dates.extend(re.findall(pattern, text))
    
    if dates:
        extracted['date'] = dates[0]
        if len(dates) > 1:
            extracted['due_date'] = dates[1]
    
    # Extract currency
    currency_pattern = r'(\$|USD|EUR|GBP|INR)'
    currency_match = re.search(currency_pattern, text, re.IGNORECASE)
    if currency_match:
        extracted['currency'] = currency_match.group(1).upper()
    
    return extracted

