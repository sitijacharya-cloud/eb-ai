"""Pydantic schemas for the estimation system."""

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime


class Platform(str, Enum):
    """Supported platforms for estimation."""
    
    FLUTTER = "Flutter"
    WEB_APP = "Web App"
    API = "API"
    CMS = "CMS"


class ProjectRequirement(BaseModel):
    """Input project requirement from user."""
    
    project_name: str = Field(..., description="Name of the project")
    description: str = Field(..., description="Detailed project requirements")
    additional_context: Optional[str] = Field(None, description="Any additional context")
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_name": "E-commerce Platform",
                "description": "Build a marketplace with buyer and seller roles, product catalog, cart, and payment integration",
                "additional_context": "Need mobile app and web admin panel"
            }
        }


class AnalyzedRequirement(BaseModel):
    """Output from Analyze Requirement Agent."""
    
    project_name: str
    domain: str = Field(..., description="Project domain (e-commerce, social media, etc.)")
    features: List[str] = Field(..., description="Key features extracted")
    tech_stack: List[str] = Field(..., description="Technologies mentioned")
    platforms: List[Platform] = Field(..., description="Target platforms")
    initial_epics: List[str] = Field(..., description="Initial epics identified")
    epic_categories: Optional[Dict[str, List[str]]] = Field(default=None, description="Epic categories mapped to their related features for targeted retrieval")
    complexity: str = Field(..., description="Complexity level (simple/medium/complex)")
    user_types: Optional[List[str]] = Field(default=None, description="User roles/types in the system (e.g., Buyer, Seller)")
    special_requirements: Optional[List[str]] = Field(default=None)
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_name": "E-commerce Platform",
                "domain": "e-commerce",
                "features": ["product catalog", "shopping cart", "payment", "user authentication"],
                "tech_stack": ["Flutter", "Node.js", "PostgreSQL"],
                "platforms": ["Flutter", "API", "Web App"],
                "initial_epics": ["Authentication", "Product Management", "Order Management"],
                "epic_categories": {
                    "Authentication": ["user authentication", "login", "signup"],
                    "Product Management": ["product catalog", "product listing"],
                    "Order Management": ["shopping cart", "checkout", "order tracking"]
                },
                "complexity": "medium",
                "user_types": ["Buyer", "Seller"],
                "special_requirements": ["Real-time notifications", "Multi-currency support"]
            }
        }


class Task(BaseModel):
    """Individual task within an epic."""
    
    description: str = Field(..., description="Task description")
    efforts: Dict[Platform, int] = Field(..., description="Effort hours per platform")
    source: Optional[str] = Field(None, description="Source template/project")
    is_custom: bool = Field(False, description="Whether task is custom generated")
    
    class Config:
        json_schema_extra = {
            "example": {
                "description": "Signup with Email",
                "efforts": {
                    "Flutter": 8,
                    "API": 8,
                    "Web App": 8
                },
                "source": "Social Media Template",
                "is_custom": False
            }
        }


class Epic(BaseModel):
    """Epic containing multiple tasks."""
    
    name: str = Field(..., description="Epic name (may include user type suffix like 'Profile Management - Customer')")
    description: Optional[str] = Field(None, description="Epic description")
    tasks: List[Task] = Field(default_factory=list, description="List of tasks")
    is_mandatory: bool = Field(False, description="Whether epic is mandatory")
    source_template: Optional[str] = Field(None, description="Source template name")
    user_types: Optional[List[str]] = Field(default=None, description="User types this epic is designed for (extracted from epic name or requirements)")
    
    @property
    def total_hours(self) -> int:
        """Calculate total hours across all tasks and platforms."""
        total = 0
        for task in self.tasks:
            total += sum(task.efforts.values())
        return total
    
    @property
    def hours_by_platform(self) -> Dict[Platform, int]:
        """Calculate hours per platform."""
        platform_hours: Dict[Platform, int] = {}
        for task in self.tasks:
            for platform, hours in task.efforts.items():
                platform_hours[platform] = platform_hours.get(platform, 0) + hours
        return platform_hours
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Profile Management - Customer",
                "description": "Customer profile management features",
                "is_mandatory": False,
                "source_template": "E-commerce Template",
                "user_types": ["Customer"],
                "tasks": [
                    {
                        "description": "View and update profile",
                        "efforts": {"Flutter": 8, "API": 8},
                        "source": "E-commerce Template"
                    }
                ]
            }
        }


class ProjectEstimation(BaseModel):
    """Final project estimation output."""
    
    project_name: str
    description: str
    target_platforms: List[Platform]
    epics: List[Epic]
    generated_at: datetime = Field(default_factory=datetime.now)
    
    @property
    def total_hours(self) -> int:
        """Calculate total hours across all epics."""
        return sum(epic.total_hours for epic in self.epics)
    
    @property
    def total_hours_by_platform(self) -> Dict[Platform, int]:
        """Calculate total hours per platform."""
        platform_totals: Dict[Platform, int] = {}
        for epic in self.epics:
            for platform, hours in epic.hours_by_platform.items():
                platform_totals[platform] = platform_totals.get(platform, 0) + hours
        return platform_totals
    
    @property
    def mandatory_epics_count(self) -> int:
        """Count mandatory epics."""
        return sum(1 for epic in self.epics if epic.is_mandatory)
    
    @property
    def custom_epics_count(self) -> int:
        """Count custom epics."""
        return sum(1 for epic in self.epics if not epic.is_mandatory)
    
    def model_dump_json(self, **kwargs) -> str:
        """Override to handle datetime serialization."""
        return super().model_dump_json(**kwargs)
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_name": "E-commerce Platform",
                "description": "Marketplace with buyer/seller roles",
                "target_platforms": ["Flutter", "API", "Web App"],
                "epics": []
            }
        }


class EstimationState(BaseModel):
    """LangGraph state for estimation workflow."""
    
    # Input
    raw_requirements: ProjectRequirement
    
    # Agent Outputs
    analyzed_requirement: Optional[AnalyzedRequirement] = None
    retrieved_epics: Optional[List[Epic]] = None
    generated_epics: Optional[List[Epic]] = None  # Now includes complete epics with tasks and efforts
    final_estimation: Optional[ProjectEstimation] = None
    
    # Metadata
    validation_errors: List[str] = Field(default_factory=list)
    current_step: str = "initialized"
    retry_count: int = 0
    
    class Config:
        arbitrary_types_allowed = True


class HistoricalTemplate(BaseModel):
    """Historical project template structure."""
    
    template_name: str
    domain: str
    description: Optional[str] = None
    epics: Dict[str, Dict[str, Dict[Platform, int]]]  # epic_name -> task_desc -> platform -> hours
    
    class Config:
        json_schema_extra = {
            "example": {
                "template_name": "Social Media",
                "domain": "social_networking",
                "description": "Standard social media application template",
                "epics": {
                    "Authentication": {
                        "Signup with Email": {
                            "Flutter": 8,
                            "API": 8
                        }
                    }
                }
            }
        }
