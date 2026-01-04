"""
Task data models.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Task(BaseModel):
    """Task model for MongoDB storage."""
    
    id: Optional[str] = Field(None, alias="_id")
    document_id: str
    task_type: str  # verify_invoice, screen_candidate, review_compliance
    status: str = "pending"  # pending, in_progress, completed, failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    assigned_to: Optional[str] = None
    metadata: dict = {}
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "document_id": "507f1f77bcf86cd799439011",
                "task_type": "verify_invoice",
                "status": "pending",
                "metadata": {}
            }
        }


class TaskCreate(BaseModel):
    """Schema for creating a task."""
    document_id: str
    task_type: str
    metadata: dict = {}


class TaskResponse(BaseModel):
    """Response schema for task."""
    id: str
    document_id: str
    task_type: str
    status: str
    created_at: datetime
    updated_at: datetime
    assigned_to: Optional[str]
    metadata: dict
    
    class Config:
        from_attributes = True

