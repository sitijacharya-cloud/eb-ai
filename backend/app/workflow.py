"""LangGraph workflow orchestration for estimation system."""

import logging
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict

from .agents import (
    analyze_requirement_node,
    retrieve_similar_epic_node,
    generate_custom_epic_node,
)
from .models.schemas import ProjectRequirement, ProjectEstimation, Platform
from .services.mandatory_epics_service import get_mandatory_epics_service

logger = logging.getLogger(__name__)


class EstimationGraphState(TypedDict):
    """State for the estimation workflow graph."""
    raw_requirements: Any  # ProjectRequirement
    analyzed_requirement: Any  # AnalyzedRequirement
    retrieved_epics: Any  # List[Epic]
    generated_epics: Any  # List[Epic] - now includes tasks and efforts
    final_estimation: Any  # ProjectEstimation
    validation_errors: list
    current_step: str
    retry_count: int


def create_final_estimation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create Final Estimation - Combines all epics into ProjectEstimation.
    
    Agent 3 (generate_custom_epic) already provides complete epics with tasks and efforts.
    This node simply aggregates them into the final ProjectEstimation object.
    
    Args:
        state: Current state with generated_epics
        
    Returns:
        Updated state with final_estimation
    """
    logger.info("=== Create Final Estimation ===")
    
    try:
        raw_requirements = state.get("raw_requirements")
        analyzed_req = state.get("analyzed_requirement")
        generated_epics = state.get("generated_epics", [])
        
        if not generated_epics:
            logger.error("No epics generated")
            return {
                "current_step": "error",
                "validation_errors": ["No epics available for estimation"]
            }
        
        # All epics already have complete tasks with effort estimates from Agent 3
        all_epics = generated_epics
        
        # Create final estimation
        final_estimation = ProjectEstimation(
            project_name=raw_requirements.project_name,
            description=raw_requirements.description,
            epics=all_epics,
            target_platforms=analyzed_req.platforms if analyzed_req else []
        )
        
        # Log summary
        total_hours = final_estimation.total_hours
        platform_totals = final_estimation.total_hours_by_platform
        
        logger.info(f"✓ Final Estimation Created:")
        logger.info(f"  - Total Hours: {total_hours}")
        logger.info(f"  - Total Epics: {len(all_epics)}")
        logger.info(f"  - Mandatory epics: {final_estimation.mandatory_epics_count}")
        logger.info(f"  - Custom epics: {final_estimation.custom_epics_count}")
        logger.info(f"  - Platform breakdown: {dict(platform_totals)}")
        
        return {
            "final_estimation": final_estimation,
            "current_step": "final_estimation_created"
        }
        
    except Exception as e:
        logger.error(f"Failed to create final estimation: {e}")
        return {
            "current_step": "error",
            "validation_errors": [f"Estimation creation failed: {str(e)}"]
        }



def validate_output_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validation Node - Ensures business rules compliance.
    
    Checks:
    1. All mandatory epics present
    2. Each epic has tasks
    3. Total effort is reasonable
    4. Platform assignments valid
    
    Args:
        state: Current state
        
    Returns:
        Updated state with validation results
    """
    logger.info("=== Validate Output ===")
    
    final_estimation = state.get("final_estimation")
    
    if not final_estimation:
        return {
            "validation_errors": ["No final estimation generated"],
            "current_step": "validation_failed"
        }
    
    errors = []
    warnings = []
    
    # Check 1: Mandatory epics (load from service to stay in sync with JSON)
    epic_names = [epic.name for epic in final_estimation.epics]
    mandatory_epic_service = get_mandatory_epics_service()
    mandatory_epic_names = mandatory_epic_service.get_mandatory_epic_names()
    missing_mandatory = [name for name in mandatory_epic_names if name not in epic_names]
    
    if missing_mandatory:
        warnings.append(f"Missing mandatory epics: {missing_mandatory}")
    
    # Check 2: Each epic has tasks
    empty_epics = [epic.name for epic in final_estimation.epics if not epic.tasks]
    if empty_epics:
        warnings.append(f"Epics with no tasks: {empty_epics}")
    
    # Check 3: Reasonable total effort (50-10000 hours)
    total_hours = final_estimation.total_hours
    if total_hours < 10:
        errors.append(f"Total effort too low: {total_hours} hours")
    elif total_hours > 20000:
        warnings.append(f"Total effort very high: {total_hours} hours")
    
    # Check 4: At least one platform
    if not final_estimation.target_platforms:
        errors.append("No target platforms specified")
    
    if errors:
        logger.error(f"Validation failed: {errors}")
        return {
            "validation_errors": errors + warnings,
            "current_step": "validation_failed"
        }
    
    if warnings:
        logger.warning(f"Validation warnings: {warnings}")
    
    logger.info(f"✓ Validation passed (with {len(warnings)} warnings)")
    
    return {
        "validation_errors": warnings,  # Store warnings
        "current_step": "validation_passed"
    }


def should_retry(state: Dict[str, Any]) -> str:
    """Decide whether to retry or end based on validation."""
    current_step = state.get("current_step", "")
    retry_count = state.get("retry_count", 0)
    
    if current_step == "validation_failed" and retry_count < 2:
        logger.warning(f"Validation failed, retry {retry_count + 1}")
        return "retry"
    
    if current_step == "error":
        logger.error("Error state reached")
        return "end"
    
    return "end"


def build_estimation_graph() -> StateGraph:
    """
    Build the LangGraph workflow for estimation.
    
    Workflow (Optimized 3-Agent):
    1. Analyze Requirement
    2. Retrieve Similar Epics (mandatory + MySQL retrieval)
    3. Generate Custom Epics (with tasks and effort estimates)
    4. Create Final Estimation (aggregate all epics)
    5. Validate Output
    6. End
    
    Returns:
        Compiled StateGraph
    """
    # Create graph
    workflow = StateGraph(EstimationGraphState)
    
    # Add nodes
    workflow.add_node("analyze_requirement", analyze_requirement_node)
    workflow.add_node("retrieve_similar_epics", retrieve_similar_epic_node)
    workflow.add_node("generate_custom_epics", generate_custom_epic_node)
    workflow.add_node("create_final_estimation", create_final_estimation_node)
    workflow.add_node("validate_output", validate_output_node)
    
    # Set entry point
    workflow.set_entry_point("analyze_requirement")
    
    # Add edges
    workflow.add_edge("analyze_requirement", "retrieve_similar_epics")
    workflow.add_edge("retrieve_similar_epics", "generate_custom_epics")
    workflow.add_edge("generate_custom_epics", "create_final_estimation")
    workflow.add_edge("create_final_estimation", "validate_output")
    
    # Conditional edge from validation
    workflow.add_conditional_edges(
        "validate_output",
        should_retry,
        {
            "retry": "generate_custom_epics",  # Retry from custom epic generation
            "end": END
        }
    )
    
    # Compile graph
    app = workflow.compile()
    
    logger.info("✓ Estimation graph compiled successfully (3-agent workflow)")
    
    return app


def run_estimation_workflow(project_requirement: ProjectRequirement):
    """
    Run the complete estimation workflow.
    
    Args:
        project_requirement: User's project requirement
        
    Returns:
        Tuple of (ProjectEstimation, AnalyzedRequirement)
        
    Raises:
        Exception if workflow fails
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"Starting estimation workflow for: {project_requirement.project_name}")
    logger.info(f"{'='*60}\n")
    
    # Build graph
    app = build_estimation_graph()
    
    # Initialize state
    initial_state = {
        "raw_requirements": project_requirement,
        "analyzed_requirement": None,
        "retrieved_epics": None,
        "generated_epics": None,  # Now includes complete epics with tasks and efforts
        "final_estimation": None,
        "validation_errors": [],
        "current_step": "initialized",
        "retry_count": 0
    }
    
    try:
        # Run workflow
        final_state = app.invoke(initial_state)
        
        # Extract final estimation and analyzed requirement
        final_estimation = final_state.get("final_estimation")
        analyzed_requirement = final_state.get("analyzed_requirement")
        
        if not final_estimation:
            errors = final_state.get("validation_errors", ["Unknown error"])
            raise Exception(f"Workflow failed: {errors}")
        
        validation_errors = final_state.get("validation_errors", [])
        if validation_errors:
            logger.warning(f"Estimation completed with warnings: {validation_errors}")
        
        logger.info(f"\n{'='*60}")
        logger.info(f"✓ Estimation workflow completed successfully")
        logger.info(f"{'='*60}\n")
        
        return final_estimation, analyzed_requirement
        
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        raise


# Export
__all__ = ["run_estimation_workflow", "build_estimation_graph"]
