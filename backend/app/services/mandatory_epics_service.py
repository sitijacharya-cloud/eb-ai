"""Service to load mandatory epics from configuration file."""

import json
import logging
from pathlib import Path
from typing import List, Dict

from ..models.schemas import Epic, Task, Platform

logger = logging.getLogger(__name__)


class MandatoryEpicsService:
    """Service to manage mandatory epics from JSON configuration."""
    
    def __init__(self, config_path: str = None):
        """
        Initialize the service.
        
        Args:
            config_path: Path to mandatory_epics.json, defaults to app/data/mandatory_epics.json
        """
        if config_path is None:
            # Default path relative to this file
            config_path = Path(__file__).parent.parent / "data" / "mandatory_epics.json"
        
        self.config_path = Path(config_path)
        self._mandatory_epics = None
    
    def _load_config(self) -> Dict:
        """Load mandatory epics configuration from JSON file."""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            return config
        except FileNotFoundError:
            logger.error(f"Mandatory epics config not found: {self.config_path}")
            return {"mandatory_epics": []}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in mandatory epics config: {e}")
            return {"mandatory_epics": []}
    
    def get_mandatory_epics(self) -> List[Epic]:
        """
        Get all mandatory epics with their tasks and hours.
        
        Returns:
            List of Epic objects with fixed tasks and hours
        """
        if self._mandatory_epics is not None:
            return self._mandatory_epics
        
        config = self._load_config()
        epics = []
        
        for epic_data in config.get("mandatory_epics", []):
            try:
                # Convert tasks
                tasks = []
                for task_data in epic_data.get("tasks", []):
                    # Convert platform names to Platform enum and hours to int
                    efforts = {}
                    for platform_name, hours in task_data.get("efforts", {}).items():
                        try:
                            platform = Platform(platform_name)
                            efforts[platform] = int(hours)
                        except ValueError:
                            logger.warning(f"Unknown platform '{platform_name}' in mandatory epic '{epic_data['name']}'")
                            continue
                    
                    if efforts:
                        task = Task(
                            description=task_data["description"],
                            efforts=efforts,
                            source="mandatory_config",
                            is_custom=False
                        )
                        tasks.append(task)
                
                # Create Epic object
                epic = Epic(
                    name=epic_data["name"],
                    description=epic_data.get("description", ""),
                    tasks=tasks,
                    is_mandatory=True,
                    source_template="mandatory_config"
                )
                epics.append(epic)
                
                logger.debug(f"Loaded mandatory epic: {epic.name} with {len(tasks)} tasks")
                
            except Exception as e:
                logger.error(f"Error loading mandatory epic '{epic_data.get('name', 'unknown')}': {e}")
                continue
        
        self._mandatory_epics = epics
        logger.info(f"Loaded {len(epics)} mandatory epics from config")
        
        return epics
    
    def get_mandatory_epic_names(self) -> List[str]:
        """Get list of mandatory epic names."""
        epics = self.get_mandatory_epics()
        return [epic.name for epic in epics]


# Singleton instance
_mandatory_epics_service = None


def get_mandatory_epics_service() -> MandatoryEpicsService:
    """Get singleton instance of MandatoryEpicsService."""
    global _mandatory_epics_service
    if _mandatory_epics_service is None:
        _mandatory_epics_service = MandatoryEpicsService()
    return _mandatory_epics_service
