# backend/exercises/tests/test_repositories.py
from django.test import TestCase

from exercises.models import Exercise
from exercises.repositories import ExerciseRepository


class ExerciseRepositoryTests(TestCase):
    def setUp(self) -> None:
        # Create a small sample set (independent from fixtures)
        Exercise.objects.create(
            id="ex1",
            name="Example 1",
            description="Desc 1",
            muscle_groups=["legs"],
            equipment_required=[],
            contraindications=[],
            estimated_calories_per_min=3.5,
            intensity=Exercise.INTENSITY_LOW,
        )
        Exercise.objects.create(
            id="ex2",
            name="Example 2",
            description="Desc 2",
            muscle_groups=["core"],
            equipment_required=[],
            contraindications=["back"],
            estimated_calories_per_min=6.0,
            intensity=Exercise.INTENSITY_MEDIUM,
        )

    def test_list_all_returns_all_exercises(self) -> None:
        exercises = ExerciseRepository.list_all()
        ids = {e.id for e in exercises}
        self.assertEqual(ids, {"ex1", "ex2"})

    def test_get_by_ids_filters_correctly(self) -> None:
        exercises = ExerciseRepository.get_by_ids(["ex2"])
        self.assertEqual(len(exercises), 1)
        self.assertEqual(exercises[0].id, "ex2")

    def test_get_by_ids_empty_iterable_returns_empty_list(self) -> None:
        exercises = ExerciseRepository.get_by_ids([])
        self.assertEqual(exercises, [])

    def test_to_llm_payload_matches_model_fields(self) -> None:
        exercises = ExerciseRepository.list_all()
        payload = ExerciseRepository.to_llm_payload(exercises)

        # Sanity: same length, id field present, and intensity set from model.intensity
        self.assertEqual(len(payload), len(exercises))
        for p, e in zip(payload, exercises):
            self.assertEqual(p["id"], e.id)
            self.assertEqual(p["name"], e.name)
            self.assertEqual(p["intensity"], e.intensity)
