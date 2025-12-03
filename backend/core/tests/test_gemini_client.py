# core/tests/test_gemini_client.py

from core.gemini_client import GeminiClient, GoalProfileDTO

def test_parse_goal_text(gemini_api_key):
    client = GeminiClient(gemini_api_key)

    text = "I want to burn calories but my knee hurts."
    result = client.parse_goal_text(text)

    # Basic shape checks
    assert isinstance(result, GoalProfileDTO)
    assert hasattr(result, "primary_goal")
    assert hasattr(result, "constraints")
    assert hasattr(result, "duration_seconds")

    # Behaviors we expect based on updated prompt
    assert result.primary_goal in {
        "calorie_burn",
        "general_fitness",
        "strength",
        "mobility",
        "rehab"
    }

    # Ensure injuries went to constraints, not primary goal
    assert "knee" in result.constraints.get("avoid_joint", [])

def test_generate_plan(gemini_api_key):
    client = GeminiClient(gemini_api_key)

    goal_profile = {
        "primary_goal": "calorie_burn",
        "duration_seconds": 300,
        "constraints": {
            "avoid_joint": ["knee"],
            "impact_level": "low",
            "equipment": "bodyweight_only",
        },
    }

    exercises = [
        {"id": 1, "name": "Seated Punches"},
        {"id": 2, "name": "Arm Circles"},
    ]

    result = client.generate_plan(goal_profile, exercises)

    assert hasattr(result, "plan")
    assert isinstance(result.plan, list)
    assert len(result.plan) > 0

    # Must only use allowed exercise IDs
    allowed_ids = {1, 2}
    for item in result.plan:
        assert item["exercise_id"] in allowed_ids
        assert item["duration_seconds"] > 0