"""FastAPI application for EB Estimation Agent."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import warnings

from .api import router
from .core.config import settings

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="AI-powered project estimation system using LangGraph and GPT-4"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "EB Estimation Agent API",
        "version": settings.api_version,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info(f"Starting {settings.api_title} v{settings.api_version}")
    logger.info(f"OpenAI Model: {settings.openai_model}")
    logger.info("Using MySQL for vector embeddings")
    
    # Check MySQL knowledge base stats
    try:
        from .services.mysql_knowledge_base import get_knowledge_base
        kb = get_knowledge_base()
        
        stats = kb.get_stats()
        logger.info(f"✓ MySQL Knowledge Base: {stats['total_epics']} epics from {stats['total_templates']} templates")
        logger.info(f"✓ Templates: {', '.join(stats['templates'][:5])}{'...' if len(stats['templates']) > 5 else ''}")
    except Exception as e:
        logger.error(f"MySQL Knowledge Base check failed: {e}")
        logger.warning("Templates may need to be loaded. Run: python -m backend.app.services.mysql_knowledge_base init")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Shutting down application...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
