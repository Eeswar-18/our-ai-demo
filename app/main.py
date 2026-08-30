"""
Main FastAPI application entrypoint for our-ai-demo V0.
Serves the frontend static files and API routes.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from pathlib import Path
from app.api.v1 import health, chat

app = FastAPI(
    title="our-ai-demo V0",
    description="AI business/customer-support agent demonstration",
    version="0.1.0"
)

# Include API routers
app.include_router(health.router, prefix="/v1", tags=["health"])
app.include_router(chat.router, prefix="/v1", tags=["chat"])

# Define the frontend static files directory
FRONTEND_DIST = Path("frontend/dist")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"Middleware: {request.url.path}")
    response = await call_next(request)
    return response

@app.get("/", include_in_schema=False)
async def root():
    """Serve the frontend index.html at the root."""
    print("ROOT FUNCTION CALLED")
    index_file = FRONTEND_DIST / "index.html"
    if index_file.is_file():
        return FileResponse(index_file)
    raise HTTPException(status_code=404, detail="index.html not found")

@app.get("/{path:path}", include_in_schema=False)
async def spa(path: str):
    """
    Serve static files or fallback to index.html for client-side routing.
    API routes are handled by the routers above and should not reach here.
    """
    print(f"SPA function called with path: {path}")
    # Prevent directory traversal attacks
    try:
        requested_path = (FRONTEND_DIST / path).resolve()
        # Ensure the requested path is inside the frontend dist directory
        if not requested_path.is_relative_to(FRONTEND_DIST.resolve()):
            raise HTTPException(status_code=400, detail="Invalid path")
    except (ValueError, RuntimeError):
        raise HTTPException(status_code=400, detail="Invalid path")

    # If the requested path exists as a file, serve it
    if requested_path.is_file():
        print(f"Serving file: {requested_path}")
        return FileResponse(requested_path)

    # Otherwise, serve index.html (for client-side routing)
    index_file = FRONTEND_DIST / "index.html"
    print(f"Requested path: {path}, requested_path: {requested_path}")
    print(f"Index file: {index_file}, exists: {index_file.exists()}, is_file: {index_file.is_file()}")
    if index_file.is_file():
        print(f"Serving index.html: {index_file}")
        return FileResponse(index_file)
    print("Index file not found!")
    raise HTTPException(status_code=404, detail="Index file not found")


if __name__ == "__main__":
    import uvicorn
    from app.core.config import get_settings
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development",
    )
