"""Estimation API routes."""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
import logging

from ..models.schemas import ProjectRequirement, ProjectEstimation
from ..workflow import run_estimation_workflow
from ..services.mysql_knowledge_base import get_knowledge_base

logger = logging.getLogger(__name__)

router = APIRouter(tags=["estimation"])


@router.post("/estimate", response_model=Dict[str, Any])
async def create_estimation(
    requirement: ProjectRequirement,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Generate project estimation from requirements.
    
    Args:
        requirement: Project requirement details
        background_tasks: FastAPI background tasks
        
    Returns:
        Project estimation with epics and tasks
    """
    try:
        logger.info(f"Received estimation request for: {requirement.project_name}")
        
        # Run workflow - returns both estimation and analyzed requirement
        estimation, analyzed_req = run_estimation_workflow(requirement)
        
        # Convert to dict for response
        estimation_dict = estimation.model_dump()
        
        # Add analyzed requirement to response
        if analyzed_req:
            estimation_dict['analyzed_requirement'] = analyzed_req.model_dump()
        
        result = {
            "success": True,
            "estimation": estimation_dict
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Estimation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate estimation: {str(e)}"
        )


@router.get("/epics")
async def list_epics() -> Dict[str, Any]:
    """
    Get list of all available epics in knowledge base.
    
    Returns:
        List of epic names
    """
    try:
        kb = get_knowledge_base()
        stats = kb.get_stats()
        
        return {
            "success": True,
            "total_epics": stats["total_epics"],
            "templates": stats["templates"],
            "count": stats["total_templates"]
        }
        
    except Exception as e:
        logger.error(f"Failed to list epics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve epics: {str(e)}"
        )


@router.get("/stats")
async def get_knowledge_base_stats() -> Dict[str, Any]:
    """
    Get statistics about the knowledge base.
    
    Returns:
        Knowledge base statistics
    """
    try:
        kb = get_knowledge_base()
        stats = kb.get_stats()
        
        return {
            "success": True,
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve stats: {str(e)}"
        )


@router.post("/reload-templates")
async def reload_templates() -> Dict[str, Any]:
    """
    Reload all templates from directory into MySQL knowledge base.
    
    Returns:
        Number of epics loaded
    """
    try:
        logger.info("Reloading templates into MySQL...")
        kb = get_knowledge_base()
        
        # For MySQL, we need to clear and reload via the init process
        # This is a placeholder - actual reload would need SQL truncate + load
        stats = kb.get_stats()
        
        return {
            "success": True,
            "message": f"MySQL knowledge base has {stats['total_epics']} epics from {stats['total_templates']} templates",
            "total_epics": stats['total_epics'],
            "total_templates": stats['total_templates']
        }
        
    except Exception as e:
        logger.error(f"Failed to get MySQL stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to access MySQL knowledge base: {str(e)}"
        )
