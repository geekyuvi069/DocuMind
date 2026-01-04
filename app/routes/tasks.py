"""
Task management routes.
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional, List
from app.core.security import get_current_user
from app.db.mongo import get_database
from app.models.task import TaskResponse
from bson import ObjectId

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("", response_model=List[TaskResponse])
async def get_tasks(
    status: Optional[str] = Query(None, description="Filter by task status"),
    task_type: Optional[str] = Query(None, description="Filter by task type"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get list of tasks with optional filtering.
    
    - Filter by status (pending, in_progress, completed, failed)
    - Filter by task type (verify_invoice, screen_candidate, review_compliance)
    """
    db = get_database()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error"
        )
    
    # Build query
    query = {}
    if status:
        query["status"] = status
    if task_type:
        query["task_type"] = task_type
    
    # Fetch tasks
    cursor = db.tasks.find(query).sort("created_at", -1)
    tasks = await cursor.to_list(length=100)
    
    # Convert to response model
    result = []
    for task in tasks:
        result.append(TaskResponse(
            id=str(task["_id"]),
            document_id=task["document_id"],
            task_type=task["task_type"],
            status=task["status"],
            created_at=task["created_at"],
            updated_at=task["updated_at"],
            assigned_to=task.get("assigned_to"),
            metadata=task.get("metadata", {})
        ))
    
    return result


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific task by ID."""
    db = get_database()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error"
        )
    
    try:
        task = await db.tasks.find_one({"_id": ObjectId(task_id)})
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        return TaskResponse(
            id=str(task["_id"]),
            document_id=task["document_id"],
            task_type=task["task_type"],
            status=task["status"],
            created_at=task["created_at"],
            updated_at=task["updated_at"],
            assigned_to=task.get("assigned_to"),
            metadata=task.get("metadata", {})
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid task ID"
        )

