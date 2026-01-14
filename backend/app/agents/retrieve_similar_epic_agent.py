import logging
from typing import Dict, Any, List

from ..models.schemas import  Epic
from ..services.mysql_knowledge_base import get_knowledge_base
from ..services.mandatory_epics_service import get_mandatory_epics_service
from ..utils.epic_utils import is_similar_epic_name

logger = logging.getLogger(__name__)


def retrieve_similar_epic_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Find similar epics from historical data using vector search.
    
    Retrieves all mandatory epics plus relevant epics from MySQL
    based on similarity to the current project requirements.
    """
    logger.info("=== Retrieve Similar Epic Agent ===")
    
    analyzed_req = state["analyzed_requirement"]
    
    if not analyzed_req:
        logger.error("No analyzed requirement found")
        return {
            "validation_errors": ["Missing analyzed requirement"],
            "current_step": "error"
        }
    
    try:
        # Initialize services
        kb = get_knowledge_base()
        mandatory_service = get_mandatory_epics_service()
        
        retrieved_epics: List[Epic] = []
        mandatory_epic_names = set()
        
        # Step 1: Load ALL mandatory epics from config (with fixed tasks and hours)
        logger.info("Loading mandatory epics from configuration...")
        mandatory_epics = mandatory_service.get_mandatory_epics()
        
        for epic in mandatory_epics:
            retrieved_epics.append(epic)
            mandatory_epic_names.add(epic.name)
            logger.info(f"  ✓ Loaded mandatory epic: {epic.name} ({len(epic.tasks)} tasks, source: {epic.source_template})")
        
        logger.info(f"✓ Loaded {len(mandatory_epics)} mandatory epics with fixed tasks and hours")
        
        # Step 2: Retrieve epics separately for each epic category
        
        epic_categories = analyzed_req.epic_categories or {}
        
        # Track all epic names we've added (for semantic deduplication)
        added_epic_names = list(mandatory_epic_names)
        
        if epic_categories:
            logger.info(f"Retrieving epics separately for {len(epic_categories)} categories...")
            
            for epic_name, related_features in epic_categories.items():
                # Skip retrieval if this category name matches a mandatory epic
                # (Mandatory epics are already included from config)
                if epic_name in mandatory_epic_names or any(is_similar_epic_name(epic_name, m) for m in mandatory_epic_names):
                    logger.info(f"  ⊗ Skipped category '{epic_name}': Already in mandatory epics")
                    continue
                
                # Build focused query for this specific epic category
                query_text = f"Epic: {epic_name}. Features: {', '.join(related_features)}"
                logger.info(f"  Querying category '{epic_name}': {query_text}")
                
                # Retrieve epics for this specific category
                category_epics = kb.retrieve_similar_epics(
                    query_text=query_text,
                    n_results=5,  # Get top 3 for each category
                    similarity_threshold=0.4 #0-disimilar , 1-similar 
                )
                
                # Filter out duplicates
                for epic in category_epics:
                    # Skip if exact match with mandatory epic
                    if epic.name in mandatory_epic_names:
                        logger.info(f"    - Skipped: {epic.name} (mandatory)")
                        continue
                    
                    # Check for semantic similarity with any already-added epic
                    is_duplicate = False
                    for existing_name in added_epic_names:
                        if is_similar_epic_name(epic.name, existing_name):
                            logger.info(f"    - Skipped: {epic.name} (similar to {existing_name})")
                            is_duplicate = True
                            break
                    
                    if not is_duplicate:
                        retrieved_epics.append(epic)
                        added_epic_names.append(epic.name)
                        logger.info(f"    + Added: {epic.name} (from {epic.source_template}, {len(epic.tasks)} tasks)")
        
        else:
            # Fallback: Use combined query if no epic_categories available
            logger.warning("No epic_categories found, using fallback combined query")
            query_parts = [
                f"Project domain: {analyzed_req.domain}",
                f"Features: {', '.join(analyzed_req.features)}",
                f"Initial epics: {', '.join(analyzed_req.initial_epics)}"
            ]
            query_text = ". ".join(query_parts)
            
            logger.info(f"Searching with combined query: {query_text[:100]}...")
            
            similar_epics = kb.retrieve_similar_epics(
                query_text=query_text,
                n_results=25
            )
            
            # Filter out duplicates
            for epic in similar_epics:
                if epic.name in mandatory_epic_names:
                    logger.info(f"  - Skipped: {epic.name} (mandatory)")
                    continue
                
                is_duplicate = False
                for existing_name in added_epic_names:
                    if is_similar_epic_name(epic.name, existing_name):
                        logger.info(f"  - Skipped: {epic.name} (similar to {existing_name})")
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    retrieved_epics.append(epic)
                    added_epic_names.append(epic.name)
                    logger.info(f"  + Added: {epic.name} (from {epic.source_template})")
        
        logger.info(f"✓ Retrieved {len(retrieved_epics)} total epics:")
        logger.info(f"  - {len(mandatory_epic_names)} mandatory")
        logger.info(f"  - {len(retrieved_epics) - len(mandatory_epic_names)} similar (after deduplication)")

        # Filter tasks and efforts by target platforms
        target_platforms = state["analyzed_requirement"].platforms
        # Create a set of platform enums for comparison
        target_platform_set = set(target_platforms)
        logger.info(f" Filtering epics for target platforms: {[p.value for p in target_platforms]}")
        
        filtered_epics = []
        for epic in retrieved_epics:
            filtered_tasks = []
            for task in epic.tasks:
                # Keep only efforts for target platforms
                # Note: task.efforts keys are Platform enum objects
                filtered_efforts = {
                    platform: hours 
                    for platform, hours in task.efforts.items() 
                    if platform in target_platform_set
                }
                
                # Only include task if it has at least one relevant platform
                if filtered_efforts:
                    task.efforts = filtered_efforts
                    filtered_tasks.append(task)
            
            # Only include epic if it has at least one relevant task
            if filtered_tasks:
                epic.tasks = filtered_tasks
                filtered_epics.append(epic)
                logger.info(f"  ✓ {epic.name}: {len(filtered_tasks)} tasks (filtered by platform)")
            else:
                logger.info(f"  ✗ {epic.name}: Excluded (no tasks for target platforms)")
        
        logger.info(f"✓ Final result: {len(filtered_epics)} epics with platform-filtered tasks")
        
        return {
            "retrieved_epics": filtered_epics,
            "current_step": "retrieve_similar_epics_complete"
        }
        
    except Exception as e:
        logger.error(f"Error in retrieve_similar_epic_node: {e}")
        return {
            "validation_errors": [f"Failed to retrieve epics: {str(e)}"],
            "current_step": "error"
        }
