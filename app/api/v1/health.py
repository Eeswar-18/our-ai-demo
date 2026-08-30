"""
Health, audit, and business context endpoints for our-ai-demo V0.
"""

from fastapi import APIRouter, Query, HTTPException, Body
from app.core.audit_logger import AuditLogger
import json
import os
from pathlib import Path

router = APIRouter()


@router.get("/health")
async def health_check():
    """Return a simple health status."""
    return {"status": "healthy", "service": "our-ai-demo V0"}


@router.get("/audit-logs")
async def get_audit_logs(limit: int = Query(100, ge=1, le=1000)):
    """Return recent audit log entries for monitoring and debugging."""
    logs = AuditLogger.get_recent_logs(limit=limit)
    # Parse the JSON strings back to objects for easier consumption
    import json
    parsed_logs = [json.loads(log) for log in logs]
    return {
        "logs": parsed_logs,
        "count": len(parsed_logs),
        "limit": limit
    }


@router.put("/business-context")
async def update_business_context(context: dict = Body(...)):
    """Update the business context JSON file.
    This allows updating the business context without restarting the application.
    """
    # Define the path to the business context file
    # Go up three levels from this file to reach the project root, then to data/business.json
    context_file = Path(__file__).parents[3] / "data" / "business.json"
    
    # Ensure the directory exists
    context_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Write the new context to the file
        with open(context_file, 'w', encoding='utf-8') as f:
            json.dump(context, f, indent=2)
        
        # Verify that the file was written correctly by reading it back
        with open(context_file, 'r', encoding='utf-8') as f:
            written_context = json.load(f)
        
        return {
            "status": "success",
            "message": "Business context updated successfully",
            "context": written_context
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update business context: {str(e)}")
