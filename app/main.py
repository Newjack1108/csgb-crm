from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.core.config import settings
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

# Serve static files (frontend)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/health")
async def health():
    return {"status": "healthy"}


# Serve frontend for all non-API routes (must be last)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Skip API routes, docs, and static files - these are handled by FastAPI
        if any(full_path.startswith(prefix) for prefix in [
            "api", "docs", "redoc", "openapi.json", "health", "static"
        ]):
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Not found")
        
        index_path = os.path.join(static_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"message": "Frontend not built. Run 'npm run build' in frontend directory."}
