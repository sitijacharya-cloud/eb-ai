import logging
from typing import Dict, Any

from ..models.schemas import AnalyzedRequirement, Platform
from ..services.openai_service import get_openai_service
from ..core.constants import ANALYZE_REQUIREMENT_PROMPT

logger = logging.getLogger(__name__)


def analyze_requirement_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze user requirements and extract structured information.
    
    Extracts features, tech stack, platforms, epics, user types,
    and special requirements from raw project description.
    """
    logger.info("=== Analyze Requirement Agent ===")
    
    raw_requirements = state["raw_requirements"]
    
    # Build requirement text for analysis
    requirement_text = f"""
Project Name: {raw_requirements.project_name}
Description: {raw_requirements.description}
Additional Context: {raw_requirements.additional_context or 'None'}
    """.strip()
    
    prompt = ANALYZE_REQUIREMENT_PROMPT.format(requirement=requirement_text)
    
    try:
        # Get OpenAI service
        openai_service = get_openai_service()
        
        # Generate analysis
        logger.info("Calling OpenAI to analyze requirements...")
        analysis_json = openai_service.generate_json_completion(
            prompt=prompt,
            system_message="""You are an experienced software architect. Analyze requirements thoroughly and extract structured information.

 CRITICAL: Platform Selection Rules (READ CAREFULLY):

1. END USER PLATFORMS:
   - Mobile App / Android / iOS → Use "Flutter"
   - Web Application for users → Use "Web App"

2. ADMIN PLATFORMS:
   - Admin Dashboard / Admin Panel / Web-based dashboard / Management Console → Use "CMS"
   -  DO NOT use "Web App" for admin dashboards - use "CMS"


Return only valid JSON."""
        )
        
        logger.info(f"Analysis result: {analysis_json}")
        
        # Convert platforms to Platform enum with flexible matching
        platforms = []
        platform_mapping = {
            "flutter": Platform.FLUTTER,
            "mobile app": Platform.FLUTTER,
            "mobile application": Platform.FLUTTER,
            "mobile": Platform.FLUTTER,
            "android": Platform.FLUTTER,
            "ios": Platform.FLUTTER,
            "web based app": Platform.WEB_APP,
            "webapp": Platform.WEB_APP,
            "web": Platform.WEB_APP,
            "web application": Platform.WEB_APP,
            "api": Platform.API,
            "backend": Platform.API,
            "web service": Platform.API,
            "webservice": Platform.API,
            "cms": Platform.CMS,
            "admin": Platform.CMS,
            "admin panel": Platform.CMS,
            "admin dashboard": Platform.CMS,
            "management console": Platform.CMS,
            "admin portal": Platform.CMS,
            "web-based dashboard": Platform.CMS,
            "web dashboard": Platform.CMS
        }
        
        for platform_str in analysis_json.get("platforms", []):
            # Try exact match first
            try:
                platform = Platform(platform_str)
                platforms.append(platform)
            except ValueError:
                # Try flexible matching
                platform_lower = platform_str.lower().strip()
                if platform_lower in platform_mapping:
                    platforms.append(platform_mapping[platform_lower])
                    logger.info(f"Mapped '{platform_str}' to {platform_mapping[platform_lower].value}")
                else:
                    logger.warning(f"Unknown platform: {platform_str}, skipping")
        
        # POST-PROCESSING: 
        # If Web App is detected but requirement mentions mobile/android/ios, likely meant Flutter
        requirement_lower = requirement_text.lower()
        has_mobile_keywords = any(keyword in requirement_lower for keyword in [
            "mobile app", "android", "ios", "mobile application", "mobile device"
        ])
        has_web_user_keywords = any(keyword in requirement_lower for keyword in [
            "web application for users", "web app for users", "browser-based app", 
            "users access via browser", "web-based application for customers",
            "responsive web application", "responsive web app", "web application enabling users",
            "web app enabling users", "across devices", "mobile and web", "mobile apps as well as",
            "in addition to mobile", "along with a web"
        ])
        has_admin_keywords = any(keyword in requirement_lower for keyword in [
            "admin dashboard", "web-based dashboard", "admin panel", "management console",
            "admin portal", "web dashboard for admin", "admins will have access to a web"
        ])
        
        # Correction logic
        if Platform.WEB_APP in platforms:
            # If mobile app is mentioned and Web App is detected, check if it's actually admin dashboard
            if has_mobile_keywords and not has_web_user_keywords:
                if has_admin_keywords:
                    logger.warning(f" CORRECTION: Detected 'Web App' but requirement mentions mobile + admin dashboard.")
                    logger.warning(f"   Replacing 'Web App' with 'CMS' (admin dashboard != user web app)")
                    platforms.remove(Platform.WEB_APP)
                    if Platform.CMS not in platforms:
                        platforms.append(Platform.CMS)
        
        # Ensure API is always included if any frontend platform exists
        if platforms and Platform.API not in platforms:
            platforms.append(Platform.API)
            logger.info("Auto-added API platform (required for frontend platforms)")
        
        # Create AnalyzedRequirement object
        analyzed = AnalyzedRequirement(
            project_name=raw_requirements.project_name,
            domain=analysis_json.get("domain", "general"),
            features=analysis_json.get("features", []),
            tech_stack=analysis_json.get("tech_stack", []),
            platforms=platforms,
            initial_epics=analysis_json.get("initial_epics", []),
            epic_categories=analysis_json.get("epic_categories", {}),

            user_types=analysis_json.get("user_types"),
            special_requirements=analysis_json.get("special_requirements")
        )
        
        user_types_info = f", {len(analyzed.user_types)} user types" if analyzed.user_types else ""
        epic_cat_info = f", {len(analyzed.epic_categories)} epic categories" if analyzed.epic_categories else ""
        logger.info(f"✓ Extracted {len(analyzed.features)} features, {len(analyzed.platforms)} platforms, {len(analyzed.initial_epics)} initial epics{epic_cat_info}{user_types_info}")
        
        return {
            "analyzed_requirement": analyzed,
            "current_step": "analyze_requirement_complete"
        }
        
    except Exception as e:
        logger.error(f"Error in analyze_requirement_node: {e}")
        return {
            "validation_errors": [f"Failed to analyze requirements: {str(e)}"],
            "current_step": "error"
        }
