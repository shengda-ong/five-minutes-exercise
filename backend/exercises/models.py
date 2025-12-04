# exercises/models.py
from django.db import models

class Exercise(models.Model):
    """Single exercise in the knowledge base."""

    INTENSITY_LOW = "low"
    INTENSITY_MEDIUM = "medium"
    INTENSITY_HIGH = "high"

    INTENSITY_CHOICES = [
        (INTENSITY_LOW, "Low"),
        (INTENSITY_MEDIUM, "Medium"),
        (INTENSITY_HIGH, "High"),
    ]

    id = models.CharField(
        primary_key=True,
        max_length=64,
        help_text="Stable identifier used by plans and frontend.",
    )
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)

    # Tags / metadata
    muscle_groups = models.JSONField(default=list, blank=True)
    equipment_required = models.JSONField(default=list, blank=True)
    contraindications = models.JSONField(default=list, blank=True)

    estimated_calories_per_min = models.FloatField(null=True, blank=True)
    intensity = models.CharField(
        max_length=16,
        choices=INTENSITY_CHOICES,
        default=INTENSITY_LOW,
    )

    class Meta:
        db_table = "exercise"

    def __str__(self) -> str:  # pragma: no cover
        return self.name

    def to_llm_dict(self) -> dict:
        """Shape used when sending exercises to the LLM."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "muscle_groups": self.muscle_groups,
            "equipment_required": self.equipment_required,
            "contraindications": self.contraindications,
            "estimated_calories_per_min": self.estimated_calories_per_min,
            "intensity": self.intensity,
        }


