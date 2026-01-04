"""
Workflow task management service.
"""
from typing import Optional
from datetime import datetime
from app.db.mongo import get_database
from app.models.task import TaskCreate, Task
from bson import ObjectId


async def create_task(document_id: str, document_type: str) -> Optional[str]:
    """
    Create a workflow task based on document type.
    
    Args:
        document_id: ID of the document
        document_type: Type of document (invoice, resume, legal)
        
    Returns:
        Task ID if created successfully, None otherwise
    """
    # Map document type to task type
    task_type_mapping = {
        "invoice": "verify_invoice",
        "resume": "screen_candidate",
        "legal": "review_compliance"
    }
    
    task_type = task_type_mapping.get(document_type)
    if not task_type:
        return None
    
    db = get_database()
    if db is None:
        return None
    
    # Create task
    task_data = {
        "document_id": document_id,
        "task_type": task_type,
        "status": "pending",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "metadata": {}
    }
    
    result = await db.tasks.insert_one(task_data)
    return str(result.inserted_id)


async def get_task_by_id(task_id: str) -> Optional[dict]:
    """Get task by ID."""
    db = get_database()
    if db is None:
        return None
    
    try:
        task = await db.tasks.find_one({"_id": ObjectId(task_id)})
        if task:
            task["id"] = str(task["_id"])
            del task["_id"]
        return task
    except Exception:
        return None


async def update_task_status(task_id: str, status: str) -> bool:
    """Update task status."""
    db = get_database()
    if db is None:
        return False
    
    try:
        result = await db.tasks.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": {"status": status, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0
    except Exception:
        return False

