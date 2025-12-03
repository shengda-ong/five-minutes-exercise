from google import genai
import json
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from .exceptions import AIServiceError


@dataclass
class GoalProfileDTO:
    """Data transferred from AI when interpreting user goals."""
    primary_goal: str
    duration_seconds: int
    constraints: Dict[str, Any]


@dataclass
class PlanDTO:
    """Data transferred from AI when generating a workout plan."""
    plan: List[Dict[str, Any]]
    notes: Optional[str] = None


class GeminiClient:
    """
    Wrapper around the Gemini API.
    Provides two main capabilities:

    1. parse_goal_text: natural language -> structured GoalProfileDTO
    2. generate_plan: structured plan using ONLY the given exercises

    This class is intentionally modular and testable.
    """

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        self.client = genai.Client(api_key=api_key)
        self.model = model

    # ---------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------

    def parse_goal_text(self, text: str) -> GoalProfileDTO:
        """Convert user text into a structured GoalProfile using Gemini."""
        prompt = self._build_goal_parsing_prompt(text)
        raw = self._call_model(prompt)
        parsed = self._parse_json(raw)

        try:
            return GoalProfileDTO(
                primary_goal=parsed["primary_goal"],
                duration_seconds=parsed.get("duration_seconds", 300),
                constraints=parsed.get("constraints", {})
            )
        except Exception as exc:
            raise AIServiceError(f"Invalid GoalProfile schema: {parsed}") from exc

    def generate_plan(
        self,
        goal_profile: Dict[str, Any],
        exercises: List[Dict[str, Any]]
    ) -> PlanDTO:
        """
        Given a structured goal profile and the allowed exercises,
        ask Gemini to build a 5-minute workout plan **using only those exercises**.
        """
        prompt = self._build_plan_generation_prompt(goal_profile, exercises)
        raw = self._call_model(prompt)
        parsed = self._parse_json(raw)

        try:
            return PlanDTO(
                plan=parsed["plan"],
                notes=parsed.get("notes")
            )
        except Exception as exc:
            raise AIServiceError(f"Invalid Plan schema: {parsed}") from exc

    # ---------------------------------------------------------------
    # Internal Helpers
    # ---------------------------------------------------------------

    def _call_model(self, prompt: str) -> str:
        """Send prompt to Gemini, handle errors, and return raw text."""
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            return response.text
        except Exception as exc:
            raise AIServiceError(f"Gemini model call failed: {exc}") from exc

    def _parse_json(self, text: str) -> Dict[str, Any]:
        """
        Parse JSON from Gemini output.
        Handles cases where the model wraps JSON in markdown fences.
        """

        # Strip markdown code fences if present
        cleaned = text.strip()

        # Remove ```json ... ``` or ``` ... ```
        if cleaned.startswith("```"):
            # Remove leading ```
            cleaned = cleaned.lstrip("`")
            # Remove leading 'json' if present
            cleaned = cleaned.lstrip("json").lstrip()
            # Remove trailing ```
            cleaned = cleaned.rstrip("`").strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise AIServiceError(f"Gemini did not return valid JSON: {text}") from exc

    # ---------------------------------------------------------------
    # Prompt Templates
    # ---------------------------------------------------------------

    def _build_goal_parsing_prompt(self, text: str) -> str:
        return f"""
            You are an assistant that extracts structured workout intentions.

            IMPORTANT RULES:
            - The "primary_goal" must reflect the user's FITNESS INTENTION
            (e.g., burn calories, get fitter, lose weight, etc.)
            - Injuries or limitations should NOT override the fitness intention.
            They belong ONLY under "constraints".
            - Injuries NEVER determine the primary_goal.

            Valid primary_goal values:
            - "calorie_burn"
            - "general_fitness"
            - "strength"
            - "mobility"
            - "rehab"  (Only choose this if the user explicitly says they want rehabilitation.)

            Input:
            {text}

            Return ONLY JSON in this structure:

            {{
            "primary_goal": "calorie_burn | general_fitness | strength | mobility | rehab",
            "duration_seconds": 300,
            "constraints": {{
                "avoid_joint": ["knee", "ankle", "back"],
                "impact_level": "low | medium | high",
                "equipment": "bodyweight_only | dumbbells | chair"
            }}
            }}

            Do not add explanations. JSON only.
            """.strip()

    def _build_plan_generation_prompt(self, goal_profile: Dict[str, Any], exercises: List[Dict[str, Any]]) -> str:

        return f"""
                You are an fitness coach AI assistant that builds a 5-minute workout plan.
                You MUST follow the rules strictly:

                RULES:
                - You may ONLY use exercises from the provided list.
                - Do not invent exercise names or IDs.
                - Total duration must be close to 300 seconds.
                - Keep all constraints from the goal profile.
                - Output JSON ONLY. No commentary.

                Goal Profile:
                {json.dumps(goal_profile, indent=2)}

                Allowed Exercises (each has id, name, description, etc):
                {json.dumps(exercises, indent=2)}

                Return ONLY JSON in this EXACT format:

                {{
                "plan": [
                    {{
                    "exercise_id": 1,
                    "duration_seconds": 60
                    }},
                    {{
                    "exercise_id": 5,
                    "duration_seconds": 45
                    }}
                ],
                "notes": "optional notes here"
                }}

                Do not include exercises not listed above.
                Do not include any text outside of JSON.
                """.strip()
