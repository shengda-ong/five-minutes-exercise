# exercises/repositories.py
from collections.abc import Iterable
from typing import List

from .models import Exercise


class ExerciseRepository:
    """Read access to the exercise knowledge base."""

    @staticmethod
    def list_all() -> List[Exercise]:
        return list(Exercise.objects.all())

    @staticmethod
    def get_by_ids(ids: Iterable[str]) -> List[Exercise]:
        ids_list = list(ids)
        if not ids_list:
            return []
        return list(Exercise.objects.filter(id__in=ids_list))

    @staticmethod
    def to_llm_payload(exercises: Iterable[Exercise]) -> list[dict]:
        return [e.to_llm_dict() for e in exercises]


# Example fixture sketch (place under exercises/fixtures/exercises.json)
# This is illustrative; adapt IDs and fields as needed.
# [
#   {
#     "model": "exercises.exercise",
#     "pk": "march_in_place",
#     "fields": {
#       "name": "March in Place",
#       "description": "Low intensity marching on the spot.",
#       "muscle_groups": ["legs", "cardio"],
#       "equipment_required": [],
#       "contraindications": ["knee"],
#       "estimated_calories_per_min": 4.0,
#       "intensity": "low"
#     }
#   }
# ]