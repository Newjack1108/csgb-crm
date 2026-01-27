from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

# Register routers
app.include_router(leads_router, prefix="/leads", tags=["leads"])
app.include_router(comms_router, prefix="/comms", tags=["comms"])
app.include_router(automation_router, prefix="/automation", tags=["automation"])


@app.get("/")
async def root():
    return {"message": "CSGB CRM API", "version": "0.1.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
