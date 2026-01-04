"""
PDF text extraction service.
"""
import pdfplumber
from typing import Optional
import os


async def extract_text_from_pdf(file_path: str) -> Optional[str]:
    """
    Extract text from PDF file using pdfplumber.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Extracted text as string, or None if extraction fails
    """
    try:
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None


async def save_uploaded_file(file_content: bytes, filename: str, upload_dir: str) -> str:
    """
    Save uploaded file to disk.
    
    Args:
        file_content: File content as bytes
        filename: Original filename
        upload_dir: Directory to save the file
        
    Returns:
        Path to saved file
    """
    # Create upload directory if it doesn't exist
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    import uuid
    file_ext = os.path.splitext(filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Write file
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    return file_path

