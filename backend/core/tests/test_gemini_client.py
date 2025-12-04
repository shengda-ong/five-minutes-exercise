# core/tests/test_gemini_client.py

import pytest

from core.gemini_client import (
    GeminiClient,
    GoalProfileDTO,
    PlanDTO,
)
from core.exceptions import AIServiceError


# ---------------------------------------------------------
# _parse_json
# ---------------------------------------------------------

def test_parse_json_plain():
    client = GeminiClient(api_key="dummy")
    raw = '{"foo": 1, "bar": "baz"}'

    result = client._parse_json(raw)

    assert result == {"foo": 1, "bar": "baz"}


def test_parse_json_markdown_fence():
    client = GeminiClient(api_key="dummy")
    raw = """```json
    {"foo": 1, "bar": "baz"}
    ```"""

    result = client._parse_json(raw)

    assert result == {"foo": 1, "bar": "baz"}


def test_parse_json_invalid_raises():
    client = GeminiClient(api_key="dummy")

    with pytest.raises(AIServiceError):
        client._parse_json("not valid json")


# ---------------------------------------------------------
# parse_goal_text
# ---------------------------------------------------------

def test_parse_goal_text_happy_path(monkeypatch):
    client = GeminiClient(api_key="dummy")

    def fake_call_model(prompt: str) -> str:
        return """
        {
          "primary_goal": "calorie_burn",
          "duration_seconds": 300,
          "constraints": {
            "avoid_joint": ["knee"],
            "other": ["low_impact_only"]
          }
        }
        """

    monkeypatch.setattr(client, "_call_model", fake_call_model)

    text = "I want to burn calories but my knee hurts."
    result = client.parse_goal_text(text)

    assert isinstance(result, GoalProfileDTO)
    assert result.primary_goal in {
        "calorie_burn",
        "general_fitness",
        "strength",
        "mobility",
        "rehab",
    }
    assert result.duration_seconds == 300
    assert "knee" in result.constraints.get("avoid_joint", [])


def test_parse_goal_text_invalid_schema_raises(monkeypatch):
    client = GeminiClient(api_key="dummy")

    # Missing "primary_goal" so mapping should fail
    def fake_call_model(prompt: str) -> str:
        return """
        {
          "duration_seconds": 300,
          "constraints": {}
        }
        """

    monkeypatch.setattr(client, "_call_model", fake_call_model)

    with pytest.raises(AIServiceError):
        client.parse_goal_text("anything")


# ---------------------------------------------------------
# generate_plan
# ---------------------------------------------------------

def test_generate_plan_happy_path(monkeypatch):
    client = GeminiClient(api_key="dummy")

    def fake_call_model(prompt: str) -> str:
        return """
        {
          "plan": [
            {"exercise_id": 1, "duration_seconds": 20},
            {"exercise_id": null, "duration_seconds": 5},
            {"exercise_id": 2, "duration_seconds": 20}
          ],
          "notes": "example plan"
        }
        """

    monkeypatch.setattr(client, "_call_model", fake_call_model)

    goal_profile = {
        "primary_goal": "calorie_burn",
        "duration_seconds": 300,
        "constraints": {"avoid_joint": ["knee"]},
    }
    exercises = [
        {"id": 1, "name": "March in place"},
        {"id": 2, "name": "Air punches"},
    ]

    result = client.generate_plan(goal_profile, exercises)

    assert isinstance(result, PlanDTO)
    assert isinstance(result.plan, list)
    assert len(result.plan) == 3
    assert result.notes == "example plan"

    allowed_ids = {1, 2, None}
    for block in result.plan:
        assert block["exercise_id"] in allowed_ids
        assert block["duration_seconds"] > 0


def test_generate_plan_invalid_schema_raises(monkeypatch):
    client = GeminiClient(api_key="dummy")

    # Missing "plan" key
    def fake_call_model(prompt: str) -> str:
        return """
        {
          "not_plan": []
        }
        """

    monkeypatch.setattr(client, "_call_model", fake_call_model)

    goal_profile = {
        "primary_goal": "calorie_burn",
        "duration_seconds": 300,
        "constraints": {},
    }
    exercises = []

    with pytest.raises(AIServiceError):
        client.generate_plan(goal_profile, exercises)
