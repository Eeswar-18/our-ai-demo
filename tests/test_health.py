"""
Test health and business context endpoints.
"""
import json
import os
import shutil
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app

# Backup the original business context file
BACKUP_PATH = Path("./data/business.json.backup")
CONTEXT_PATH = Path("./data/business.json")

def setup_function():
    """Backup the original business context file before each test."""
    if CONTEXT_PATH.exists():
        shutil.copy(CONTEXT_PATH, BACKUP_PATH)

def teardown_function():
    """Restore the original business context file after each test."""
    if BACKUP_PATH.exists():
        shutil.copy(BACKUP_PATH, CONTEXT_PATH)
        BACKUP_PATH.unlink()  # Remove the backup after restoring
    else:
        # If there was no backup, remove the context file if it was created during the test
        if CONTEXT_PATH.exists():
            CONTEXT_PATH.unlink()

def test_health_endpoint():
    """Test the health endpoint."""
    client = TestClient(app)
    response = client.get("/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "our-ai-demo V0"

def test_get_audit_logs_endpoint():
    """Test the audit logs endpoint."""
    client = TestClient(app)
    response = client.get("/v1/audit-logs?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "logs" in data
    assert "count" in data
    assert data["limit"] == 5
    # The logs should be a list
    assert isinstance(data["logs"], list)

def test_update_business_context_endpoint():
    """Test updating the business context."""
    client = TestClient(app)
    
    # Define a new context
    new_context = {
        "business_name": "Updated Business Name",
        "description": "Updated description.",
        "services": [],
        "faqs": [],
        "contact_information": {
            "email": "test@example.com",
            "phone": "123-456-7890",
            "website": "https://example.com"
        },
        "tone": "professional",
        "policies": {}
    }
    
    # Send the update request
    response = client.put("/v1/business-context", json=new_context)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "Business context updated successfully" in data["message"]
    assert data["context"]["business_name"] == "Updated Business Name"
    assert data["context"]["description"] == "Updated description."
    
    # Verify that the file was actually updated
    with open(CONTEXT_PATH, 'r') as f:
        file_context = json.load(f)
    assert file_context["business_name"] == "Updated Business Name"
    assert file_context["description"] == "Updated description."

def test_update_business_context_invalid_json():
    """Test updating with invalid JSON (should fail)."""
    client = TestClient(app)
    # Send invalid JSON (not a dict)
    response = client.put("/v1/business-context", json=["invalid", "list"])
    # The endpoint expects a dict, but FastAPI will validate the body and return 422 if it's not a dict
    # Actually, the endpoint expects a dict, so sending a list will cause a validation error
    assert response.status_code == 422

# Note: We are not testing other error conditions (like permission errors) for simplicity.
