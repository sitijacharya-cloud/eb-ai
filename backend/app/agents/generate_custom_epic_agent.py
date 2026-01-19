"""Generate Custom Epic Agent - Creates project-specific epics with tasks and effort estimates."""

import json
import logging
from typing import Dict, Any, List

from ..models.schemas import EstimationState, Epic, Task, Platform
from ..services.openai_service import get_openai_service
from ..core.constants import GENERATE_CUSTOM_EPIC_PROMPT
from ..utils.epic_utils import is_similar_epic_name

logger = logging.getLogger(__name__)


def validate_estimation_quality(all_epics: List[Epic], analyzed_req, features_count: int) -> List[str]:
    """
    Validate the quality of the estimation and return warnings if issues detected.
    
    Args:
        all_epics: List of all epics (mandatory + retrieved + generated)
        analyzed_req: The analyzed requirement
        features_count: Number of features in requirements
        
    Returns:
        List of warning messages (empty if all good)
    """
    warnings = []
    
    # Calculate total hours
    total_hours = 0
    for epic in all_epics:
        for task in epic.tasks:
            total_hours += sum(task.efforts.values())
    
    # Count epics
    mandatory_count = len([e for e in all_epics if e.is_mandatory])
    generated_count = len([e for e in all_epics if e.source_template == "AI Generated"])
    total_epic_count = len(all_epics)
    
    # 1. Check epic count vs features
    expected_min_epics = max(15, features_count // 2)  # At least 15, or half of features
    expected_max_epics = features_count * 2  # Up to 2x features
    
    if total_epic_count < expected_min_epics:
        warnings.append(
            f" Low epic count: {total_epic_count} epics for {features_count} features. "
            f"Expected at least {expected_min_epics}. May have insufficient coverage."
        )
    
    # 2. Check if enough custom epics were generated
    if generated_count < 15:
        warnings.append(
            f" Low custom epic generation: Only {generated_count} custom epics. "
            f"Consider generating 15-25 for comprehensive coverage."
        )
    
    # 3. Check platform coverage
    platforms_in_epics = set()
    for epic in all_epics:
        for task in epic.tasks:
            platforms_in_epics.update(task.efforts.keys())
    
    missing_platforms = set(analyzed_req.platforms) - platforms_in_epics
    if missing_platforms:
        warnings.append(
            f" Missing platform coverage: {[p.value for p in missing_platforms]} "
            f"have no tasks assigned."
        )
    
    # 5. Check for very small epics (might indicate lack of detail)
    small_epics = [e for e in all_epics if len(e.tasks) < 2]
    if len(small_epics) > total_epic_count * 0.3:  # More than 30% have < 2 tasks
        warnings.append(
            f" Many small epics: {len(small_epics)} epics with < 2 tasks. "
            f"Consider consolidating or adding more detail."
        )
    
    return warnings


def generate_custom_epic_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate project-specific epics with complete task breakdowns and effort estimates.
    
    This enhanced agent combines epic generation, task decomposition, and effort estimation
    into a single intelligent process that learns from retrieved epics.
    """
    logger.info("=== Generate Custom Epic Agent (Enhanced) ===")
    
    analyzed_req = state["analyzed_requirement"]
    retrieved_epics = state.get("retrieved_epics", [])
    
    if not analyzed_req:
        logger.error("No analyzed requirement found")
        return {
            "validation_errors": ["Missing analyzed requirement"],
            "current_step": "error"
        }
    
    try:
        # Separate mandatory and retrieved epics for modification
        mandatory_epics = [e for e in retrieved_epics if e.is_mandatory]
        similar_epics = [e for e in retrieved_epics if not e.is_mandatory]
        
        logger.info(f"Starting with {len(retrieved_epics)} epics from retrieval")
        logger.info(f"  - Mandatory (unchanged): {len(mandatory_epics)}")
        logger.info(f"  - Retrieved (will be modified): {len(similar_epics)}")
        
        # We'll build all_epics progressively: mandatory unchanged -> retrieved modified -> new custom
        all_epics: List[Epic] = []
        existing_epic_names = []
        
        # Add mandatory epics unchanged
        for mandatory_epic in mandatory_epics:
            all_epics.append(mandatory_epic)
            existing_epic_names.append(mandatory_epic.name)
            logger.info(f"  ✓ Kept mandatory unchanged: {mandatory_epic.name} ({len(mandatory_epic.tasks)} tasks)")
        
        # Format epics for prompt
        def format_epics_for_prompt(epics: List[Epic], limit: int = 20) -> str:
            lines = []
            for epic in epics[:limit]:
                lines.append(f"\n**{epic.name}** ({len(epic.tasks)} tasks):")
                for task in epic.tasks[:5]:  # Show first 3 tasks as examples
                    platforms_str = ", ".join([f"{p.value}: {h}h" for p, h in task.efforts.items()])
                    lines.append(f"  - {task.description} → {platforms_str}")
                if len(epic.tasks) > 3:
                    lines.append(f"  - ... and {len(epic.tasks) - 3} more tasks")
            return "\n".join(lines)
        
        # Build prompt
        mandatory_summary = format_epics_for_prompt(mandatory_epics, limit=8)
        retrieved_summary = format_epics_for_prompt(similar_epics, limit=30)  # Send ALL retrieved epics
        platforms_str = ", ".join([p.value for p in analyzed_req.platforms])
        features_str = ", ".join(analyzed_req.features)
        
        # Handle user_types - can be either enum or string
        try:
            user_types_str = ", ".join([u.value if hasattr(u, 'value') else str(u) for u in analyzed_req.user_types])
        except:
            user_types_str = ", ".join([str(u) for u in analyzed_req.user_types])
        
        # Build prompt for MODIFYING retrieved epics and GENERATING new ones
        prompt = f"""You are an expert software estimator. Your task has TWO PARTS:

# PART 1: MODIFY RETRIEVED EPICS (Similar Epics Only)

The following epics were retrieved from knowledge base based on similarity. They need to be ADAPTED to match the current project requirements.

## Project Requirements:
- **Domain**: {analyzed_req.domain}
- **Target Platforms**: {platforms_str}
- **User Types**: {user_types_str}
- **Key Features**: {features_str}

## Mandatory Epics (For Reference - DO NOT MODIFY):
{mandatory_summary}

These mandatory epics are already included unchanged. Learn from their structure but don't modify them.

## Retrieved Similar Epics (MODIFY THESE):
{retrieved_summary}

**YOUR TASK FOR PART 1:**
1. Review each RETRIEVED epic (not mandatory) and its tasks
2. **PRESERVE task descriptions exactly as they are** - DO NOT rewrite or rephrase them
3. **DO NOT remove any existing tasks** - Keep all tasks from retrieved epic
4. **ONLY ADD new tasks** if project requirements specifically need them
5. **CRITICAL: Adapt platforms to match target platforms: {platforms_str}**
   - If retrieved epic has "Web App" but target is ["Flutter", "API"] → Replace "Web App" with "Flutter"
   - If retrieved epic has "Flutter" but target is ["Web App", "API", "CMS"] → Replace "Flutter" with "Web App"
   - Remove any platforms not in target list
6. Adjust effort hours based on project domain and requirements (if needed)
7. **Keep epic names EXACTLY as they are** - DO NOT rename epics
8. Keep epic descriptions as they are (minor adjustments only if needed)
9. Preserve source_template field
10. Set is_mandatory to false (these are retrieved, not mandatory)

**CRITICAL RULES:**
- ✓ Keep task descriptions verbatim: "View analytics dashboard" stays "View analytics dashboard"
- ✗ Don't rewrite: "View analytics dashboard" → "Create a dashboard view for analytics metrics" (WRONG!)
- ✓ Keep all existing tasks, don't remove any
- ✓ Only ADD tasks if project explicitly needs features not covered by existing tasks
- ✓ Keep epic names unchanged: "Analytics Dashboard - Venue" stays "Analytics Dashboard - Venue"

**Platform Adaptation Rules:**
- Examples may have different platforms than your target
- Learn task patterns and hours, but OUTPUT only target platforms: {platforms_str}
- If example shows "Flutter: 12h" and target has "Web App" → Use "Web App: 12h"
- Never include platforms outside: {platforms_str}

# PART 2: GENERATE NEW CUSTOM EPICS

{GENERATE_CUSTOM_EPIC_PROMPT.format(
            domain=analyzed_req.domain,
            project_type=analyzed_req.domain,
            platforms=platforms_str,
            user_types=user_types_str,
            features=features_str,
            mandatory_epics_summary="(Already provided above - these will be modified)",
            retrieved_epics_summary="(Already provided above - these will be modified)",
            existing_epic_names="All retrieved epics will be modified, so you can focus on NEW epics for uncovered features"
        )}

---

# OUTPUT FORMAT:

Return JSON with TWO sections:

```json
{{
  "modified_epics": [
    {{
      "name": "Original Retrieved Epic Name",  // KEEP EXACTLY AS IS
      "description": "Updated description for project context",
      "is_mandatory": false,
      "source_template": "original source",
      "tasks": [
        {{
          "description": "Original task description",  // KEEP EXACTLY AS IS - Don't rewrite!
          "efforts": {{
            "Platform1": 12,  // Adapt platform names only
            "Platform2": 16
          }}
        }},
        {{
          "description": "Another original task",  // KEEP EXACTLY AS IS
          "efforts": {{
            "Platform1": 8,
            "Platform2": 12
          }}
        }},
        {{
          "description": "New task if needed",  // ONLY if project requires additional feature
          "efforts": {{
            "Platform1": 10,
            "Platform2": 14
          }}
        }}
      ]
    }}
  ],
  "custom_epics": [
    {{
      "name": "New Epic Name - UserType",
      "description": "Brief description",
      "tasks": [
        {{
          "description": "Task description",
          "efforts": {{
            "Platform1": 12,
            "Platform2": 16
          }}
        }}
      ]
    }}
  ]
}}
```

**CRITICAL VALIDATION:**
- ALL epics (modified and custom) must ONLY use platforms from: {platforms_str}
- No platforms outside target list allowed
- modified_epics should include ALL {len(similar_epics)} retrieved similar epics (adapted, NOT mandatory)
- **CRITICAL: Task descriptions in modified_epics must be EXACTLY as in original** (no rewriting)
- **CRITICAL: Epic names in modified_epics must be EXACTLY as in original** (no renaming)
- **CRITICAL: All original tasks must be present** (don't remove tasks)
- custom_epics should be 15-25 NEW epics for uncovered features
"""
        
        # Generate custom epics with tasks and efforts
        openai_service = get_openai_service()
        logger.info("Calling OpenAI to generate custom epics with tasks and efforts...")
        
        system_message = f"""You are an expert software estimator specializing in {analyzed_req.domain} applications.

Your task has TWO PARTS:
1. MODIFY retrieved similar epics (NOT mandatory ones) to match project requirements
   - **CRITICAL: Keep task descriptions EXACTLY as they are**
   - **CRITICAL: Keep epic names EXACTLY as they are**
   - **ONLY adapt platforms and hours**
   - **ONLY ADD new tasks if project needs additional features**
   - **DO NOT remove existing tasks**
2. GENERATE new custom epics for uncovered features

 CRITICAL INSTRUCTION - PLATFORM ADAPTATION:

TARGET PLATFORMS: {platforms_str}

The examples (mandatory/retrieved epics) are REFERENCE PATTERNS showing:
 What tasks to create (epic structure, task descriptions)
 How many hours tasks typically take (effort ranges)

 But examples may have DIFFERENT platforms than your target!
 DO NOT copy platforms from examples!

YOUR JOB:
1. Learn TASK PATTERNS from examples (what tasks exist in what epic, how they're described)
2. Learn EFFORT RANGES from examples (typical hours for similar work)
3. **TRANSLATE to your target platforms: {platforms_str}**
4. If example shows "Web App: 12h" but your target is Flutter → Output "Flutter: 12h"
5. If example shows platforms not in target → Skip those platforms
6. **ONLY include platforms from: {platforms_str}**

Think of examples as TEMPLATES to adapt, not blueprints to copy exactly.

 CRITICAL INSTRUCTION - EPIC NAMING WITH USER TYPES:

USER TYPES IN PROJECT: {user_types_str}

**Epic Naming Rules:**
1. **Generic epics** (used by all users) → Use plain name
   Examples: "Authentication", "Database Design", "Notification", "Payment Integration"

2. **User-specific epics** (specific to one user type) → Add "- UserType" suffix
   Examples: "Profile Management - Customer", "Dashboard - Admin", "Order Management - Seller"

3. **Multiple user types** → Use "/" separator
   Examples: "Messaging - Buyer/Seller", "Reviews - Customer/Vendor"

**Decision Logic:**
- If ALL user types use the feature → Generic name (e.g., "Authentication")
- If SPECIFIC user types use the feature → Add user type (e.g., "Dashboard - Admin")
- If feature differs per user type → Create separate epic per type

**WHY:** Shows feature ownership, groups by user journey, improves retrieval accuracy.

 COVERAGE REQUIREMENT:
Generate **15-25 custom epics** to ensure comprehensive coverage of all features.

Analyze the features list carefully: {features_str}

**CRITICAL: Map every major feature to epics:**
- Break down complex feature areas into multiple focused epics
- Each payment method → Separate epic (if multiple payment methods exist)
- Each AI/ML capability → Separate epic (Prediction, Recommendation, Detection, Analysis)
- Each integration → Separate epic (Google Classroom, Canvas, Turnitin, etc.)
- Each major user flow → Separate epic (Onboarding, Profile, Dashboard, Settings)
- Platform-specific features → Separate epics (Offline Sync, Localization, Location Services)
- Admin features → Multiple epics (Dashboard, User Mgmt, Billing, Analytics, Compliance)
- Content management → Separate epics (CMS Pages, Email Templates, File Uploads)

**Epic Count Guidelines:**
- 10-20 features in requirements → Generate 15-20 epics
- 20-40 features in requirements → Generate 20-30 epics
- 40+ features in requirements → Generate 30-40 epics

Key responsibilities:
- Generate **15-25 domain-specific epics** for {analyzed_req.domain}
- **Use "Epic Name - UserType" format when epic is user-specific**
- Ensure ALL features from requirements are covered (study features list exhaustively)
- Adapt example patterns to target platforms: {platforms_str}
- Base effort estimates on similar tasks (but adjust platform names)
- Avoid duplicating: {', '.join(existing_epic_names[:10])}
- Each epic should have 3-8 high-level tasks (not granular sub-tasks)

Return valid JSON only."""
        
        response = openai_service.generate_json_completion(
            prompt=prompt,
            system_message=system_message
        )
        
        # Parse response
        if isinstance(response, str):
            response = json.loads(response)
        
        # Process MODIFIED epics (retrieved similar epics only, NOT mandatory)
        modified_epics_data = response.get("modified_epics", [])
        logger.info(f"Received {len(modified_epics_data)} modified retrieved epics (expected {len(similar_epics)})")
        
        for epic_data in modified_epics_data:
            epic_name = epic_data.get("name", "")
            
            # Create Task objects from tasks data
            tasks = []
            for task_data in epic_data.get("tasks", []):
                task_description = task_data.get("description", "")
                efforts_data = task_data.get("efforts", {})
                
                # Convert platform strings to Platform enum
                efforts = {}
                for platform_name, hours in efforts_data.items():
                    try:
                        platform = Platform(platform_name)
                        # Validate platform is in project requirements
                        if platform in analyzed_req.platforms:
                            efforts[platform] = int(hours)
                        else:
                            logger.warning(f"    Platform {platform_name} not in requirements for modified epic {epic_name}, skipping")
                    except ValueError:
                        logger.warning(f"    Unknown platform: {platform_name} in modified epic {epic_name}")
                        continue
                
                if efforts:  # Only add task if it has valid efforts
                    task = Task(
                        description=task_description,
                        efforts=efforts,
                        source=epic_data.get("source_template", "Modified"),
                        is_custom=False
                    )
                    tasks.append(task)
            
            # Create Epic object with preserved metadata
            if tasks:  # Only add epic if it has tasks
                modified_epic = Epic(
                    name=epic_name,
                    description=epic_data.get("description", ""),
                    tasks=tasks,
                    is_mandatory=epic_data.get("is_mandatory", False),
                    source_template=epic_data.get("source_template", "Modified")
                )
                all_epics.append(modified_epic)
                existing_epic_names.append(epic_name)
                logger.info(f"  ✓ Modified: {epic_name} ({len(tasks)} tasks, mandatory={modified_epic.is_mandatory})")
            else:
                logger.warning(f"  - Skipped modified epic: {epic_name} (no valid tasks)")
        
        logger.info(f"✓ Added {len(mandatory_epics)} mandatory epics (unchanged) and {len(modified_epics_data)} retrieved epics (modified)")
        
        # Process CUSTOM epics (new ones)
        custom_epics_data = response.get("custom_epics", [])
        logger.info(f"Received {len(custom_epics_data)} new custom epics")
        
        # Convert to Epic objects
        for epic_data in custom_epics_data:
            epic_name = epic_data.get("name", "")
            
            # Check for EXACT duplicates only (not semantic similarity)
            if epic_name in existing_epic_names:
                logger.info(f"  - Skipped: {epic_name} (exact match)")
                continue
            
            # Create Task objects from tasks data
            tasks = []
            for task_data in epic_data.get("tasks", []):
                task_description = task_data.get("description", "")
                efforts_data = task_data.get("efforts", {})
                
                # Convert platform strings to Platform enum
                efforts = {}
                for platform_name, hours in efforts_data.items():
                    try:
                        platform = Platform(platform_name)
                        # Validate platform is in project requirements
                        if platform in analyzed_req.platforms:
                            efforts[platform] = int(hours)
                        else:
                            logger.warning(f"    Platform {platform_name} not in requirements, skipping")
                    except ValueError:
                        logger.warning(f"    Unknown platform: {platform_name}")
                        continue
                
                if efforts:  # Only add task if it has valid efforts
                    task = Task(
                        description=task_description,
                        efforts=efforts,
                        source="AI Generated",
                        is_custom=True
                    )
                    tasks.append(task)
            
            # Create Epic object
            if tasks:  # Only add epic if it has tasks
                custom_epic = Epic(
                    name=epic_name,
                    description=epic_data.get("description", ""),
                    tasks=tasks,
                    is_mandatory=False,
                    source_template="AI Generated"
                )
                all_epics.append(custom_epic)
                existing_epic_names.append(epic_name)
                logger.info(f"  + Added: {epic_name} ({len(tasks)} tasks)")
            else:
                logger.warning(f"  - Skipped: {epic_name} (no valid tasks)")
        
        # Count mandatory (unchanged)
        mandatory_count = len([e for e in all_epics if e.is_mandatory])
        # Count modified retrieved epics (non-mandatory, non-AI-generated)
        modified_retrieved_count = len([e for e in all_epics if not e.is_mandatory and e.source_template not in ['AI Generated']])
        # Count new AI generated epics
        new_generated_count = len([e for e in all_epics if e.source_template == 'AI Generated'])
        
        logger.info(f"✓ Total epics: {len(all_epics)}")
        logger.info(f"  - Mandatory epics (unchanged): {mandatory_count}")
        logger.info(f"  - Retrieved epics (modified): {modified_retrieved_count}")
        logger.info(f"  - New custom epics (generated): {new_generated_count}")
        
        # Validate estimation quality
        validation_warnings = validate_estimation_quality(
            all_epics=all_epics,
            analyzed_req=analyzed_req,
            features_count=len(analyzed_req.features)
        )
        
        if validation_warnings:
            logger.warning("=== Estimation Quality Warnings ===")
            for warning in validation_warnings:
                logger.warning(warning)
        else:
            logger.info("✓ Estimation quality validation passed")
        
        return {
            "generated_epics": all_epics,
            "validation_errors": validation_warnings if validation_warnings else None,
            "current_step": "generate_custom_epics_complete"
        }
        
    except Exception as e:
        logger.error(f"Error in generate_custom_epic_node: {e}", exc_info=True)
        # If epic generation fails, continue with retrieved epics
        return {
            "generated_epics": retrieved_epics,
            "validation_errors": [f"Warning: Custom epic generation failed: {str(e)}"],
            "current_step": "generate_custom_epics_complete"
        }
