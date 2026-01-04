"""
Document management routes.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends, Query
from typing import Optional, List
from app.core.security import get_current_user
from app.core.config import settings
from app.db.mongo import get_database
from app.services.pdf_extractor import extract_text_from_pdf, save_uploaded_file
from app.services.classifier import classify_document
from app.services.extractor import extract_fields_by_type
from app.services.workflow import create_task
from app.models.document import DocumentResponse
from bson import ObjectId
from datetime import datetime

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload and process a PDF document.
    
    - Extracts text from PDF
    - Classifies document type
    - Extracts structured fields
    - Stores in MongoDB
    - Creates workflow task
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    # Read file content
    content = await file.read()
    
    # Check file size
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE / (1024*1024)}MB"
        )
    
    # Save file
    file_path = await save_uploaded_file(content, file.filename, settings.UPLOAD_DIR)
    
    try:
        # Extract text
        raw_text = await extract_text_from_pdf(file_path)
        if not raw_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract text from PDF"
            )
        
        # Classify document
        document_type = classify_document(raw_text)
        
        # Extract fields
        extracted_fields = await extract_fields_by_type(document_type, raw_text)
        
        # Store in database
        db = get_database()
        if db is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection error"
            )
        
        document_data = {
            "filename": file.filename,
            "file_path": file_path,
            "document_type": document_type,
            "raw_text": raw_text,
            "extracted_fields": extracted_fields,
            "uploaded_by": current_user["username"],
            "uploaded_at": datetime.utcnow(),
            "status": "processed"
        }
        
        result = await db.documents.insert_one(document_data)
        document_id = str(result.inserted_id)
        
        # Create workflow task
        await create_task(document_id, document_type)
        
        # Return response
        return DocumentResponse(
            id=document_id,
            filename=document_data["filename"],
            document_type=document_data["document_type"],
            extracted_fields=document_data["extracted_fields"],
            uploaded_by=document_data["uploaded_by"],
            uploaded_at=document_data["uploaded_at"],
            status=document_data["status"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing document: {str(e)}"
        )


@router.get("", response_model=List[DocumentResponse])
async def get_documents(
    type: Optional[str] = Query(None, description="Filter by document type"),
    skill: Optional[str] = Query(None, description="Filter resumes by skill"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get list of documents with optional filtering.
    
    - Filter by document type
    - Filter resumes by skill
    """
    db = get_database()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error"
        )
    
    # Build query
    query = {}
    if type:
        query["document_type"] = type
    
    if skill and (not type or type == "resume"):
        # Search in extracted_fields.skills array
        query["extracted_fields.skills"] = {"$regex": skill, "$options": "i"}
        if not type:
            query["document_type"] = "resume"
    
    # Fetch documents
    cursor = db.documents.find(query).sort("uploaded_at", -1)
    documents = await cursor.to_list(length=100)
    
    # Convert to response model
    result = []
    for doc in documents:
        result.append(DocumentResponse(
            id=str(doc["_id"]),
            filename=doc["filename"],
            document_type=doc["document_type"],
            extracted_fields=doc.get("extracted_fields", {}),
            uploaded_by=doc["uploaded_by"],
            uploaded_at=doc["uploaded_at"],
            status=doc.get("status", "processed")
        ))
    
    return result


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific document by ID."""
    db = get_database()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error"
        )
    
    try:
        doc = await db.documents.find_one({"_id": ObjectId(document_id)})
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        return DocumentResponse(
            id=str(doc["_id"]),
            filename=doc["filename"],
            document_type=doc["document_type"],
            extracted_fields=doc.get("extracted_fields", {}),
            uploaded_by=doc["uploaded_by"],
            uploaded_at=doc["uploaded_at"],
            status=doc.get("status", "processed")
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document ID"
        )

