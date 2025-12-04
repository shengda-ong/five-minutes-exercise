# core/dtos.py
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class GoalProfileDTO:
    """Structured goal profile returned from Gemini."""
    primary_goal: str                 # e.g. "calorie_burn", "general_fitness"
    intensity: str                    # "low" | "medium" | "high"
    constraints: List[str]            # e.g. ["knee injury", "no jumping"]
    additional_info: Optional[str] = None
    duration_seconds: int = 300       # keeps tests and prompts simple


@dataclass
class FilteredExercisesDTO:
    """Subset of exercise IDs that are safe/appropriate for the goal."""
    allowed_exercise_ids: List[Any]   # IDs can be int or str at this layer


@dataclass
class PlanDTO:
    """Plan structure returned from Gemini planning prompts."""
    plan: List[Dict[str, Any]]
    notes: Optional[str] = None
