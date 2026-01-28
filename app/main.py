from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from app.core.config import settings
from app.core.db import get_db
from app.modules.leads.router import router as leads_router
from app.modules.comms.router import router as comms_router
from app.modules.automation.router import router as automation_router

app = FastAPI(
    title="CSGB CRM",
    description="Modular Monolith MVP CRM",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers with /api prefix
app.include_router(leads_router, prefix="/api/leads", tags=["leads"])
app.include_router(comms_router, prefix="/api/comms", tags=["comms"])
app.include_router(automation_router, prefix="/api/automation", tags=["automation"])

# Serve static files (frontend) - must be before catch-all route
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    # Mount static assets (JS, CSS, etc.)
    app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")
    # Serve other static files
    static_files = StaticFiles(directory=static_dir)
    app.mount("/static", static_files, name="static")


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/health/db")
async def health_db(db: Session = Depends(get_db)):
    """Database health check"""
    try:
        # Try a simple query
        from sqlalchemy import text
        result = db.execute(text("SELECT 1"))
        result.fetchone()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "error", "error": str(e)}


# Serve frontend for all non-API routes (must be last)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Skip API routes, docs, and static files - these are handled by FastAPI
        if any(full_path.startswith(prefix) for prefix in [
            "api", "docs", "redoc", "openapi.json", "health", "static", "assets"
        ]):
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Not found")
        
        index_path = os.path.join(static_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"message": "Frontend not built. Run 'npm run build' in frontend directory.", "static_dir": static_dir, "exists": os.path.exists(static_dir)}
else:
    # Fallback if static directory doesn't exist
    @app.get("/")
    async def root():
        static_dir_check = os.path.join(os.path.dirname(__file__), "static")
        return {
            "message": "CSGB CRM API", 
            "version": "0.1.0", 
            "frontend": "Not built",
            "static_dir": static_dir_check,
            "exists": os.path.exists(static_dir_check)
        }
