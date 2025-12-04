# Implementation Roadmap

This roadmap outlines the recommended order of implementation for **The 5 Minutes Exercise** backend.

---

## 1. Core & Infrastructure

1. **Set up Django project & basic apps**

   * Create base project and apps: `core`, `exercises`, `plans`, `api` (or use `plans.api`).
   * Configure settings, installed apps, and basic URLs.

2. **Implement `GeminiClient` in `core/`**

   * Keep it focused on:

     * Building prompts.
     * Calling Gemini.
     * Returning DTOs (`GoalProfileDTO`, `PlanDTO`, `FilteredExercisesDTO`, etc.).
   * Add tests with mocked Gemini responses.

---

## 2. Exercise Knowledge Base

3. **Design `Exercise` model in `exercises/models.py`**

   * Fields: `id`, `name`, `description`, `muscle_groups`, `estimated_calories_per_min`, `impact_level`, `contraindications`, etc.

4. **Implement `ExerciseRepository` in `exercises/repositories.py`**

   * Methods like `list_all()`, `get_by_ids(ids)`.

5. **Seed initial exercise data (≈30 exercises)**

   * Use fixtures or migration seeds for the prototype.

6. **Add tests for the repository & data integrity**

   * Ensure `list_all` and `get_by_ids` behave as expected.

---

## 3. Plans Domain Layer

7. **Create `plans/domain.py`**

   * Implement domain models:

     * `GoalProfile`
     * `PlanBlockType`, `PlanBlock`
     * `WorkoutPlan`

8. **Add mapping helpers between DTOs and domain objects**

   * E.g. `goal_profile_from_dto(dto)`, `workout_plan_from_dto(dto, goal_profile)`.

9. **Unit tests for domain models and mappers**

   * Focus on shape, invariants, and simple validation.

---

## 4. Agents & Services

10. **GoalUnderstandingAgent (`plans/services.py`)**

    * Uses `GeminiClient.parse_goal_text`.
    * Maps `GoalProfileDTO` → `GoalProfile`.

11. **ExerciseFilteringAgent**

    * Uses `ExerciseRepository.list_all()`.
    * Calls `GeminiClient.filter_exercises`.
    * Returns filtered exercise IDs or objects.

12. **PlanGenerationAgent**

    * Accepts `GoalProfile` + filtered exercises.
    * Calls `GeminiClient.generate_plan`.
    * Maps `PlanDTO` → `WorkoutPlan` (unvalidated).

13. **PlanValidationAgent**

    * Pure Python checks:

      * Exercise IDs exist.
      * Duration ≈ 300 seconds and not exceeding.
      * Block type/structure constraints.

14. **RecommendationService (orchestrator)**

    * Orchestrates:

      1. `GoalUnderstandingAgent`.
      2. `ExerciseFilteringAgent`.
      3. `PlanGenerationAgent`.
      4. `PlanValidationAgent`.
    * Returns final `WorkoutPlan` to API layer.

15. **Unit tests for each agent and for `RecommendationService`**

    * Mock `GeminiClient` and `ExerciseRepository`.

---

## 5. API Layer

16. **Design API serializers (if using DRF)**

    * Request: `goal_text`.
    * Response: `total_duration_seconds`, `blocks` (type, exercise_id, duration_seconds).

17. **Implement main endpoint**

    * `POST /api/v1/plans/` → uses `RecommendationService`.

18. **API tests**

    * End-to-end tests with mocked `GeminiClient`.
    * Validate JSON shape and error handling.

---

## 6. Validation, Error Handling, and Polish

19. **Error types**

    * Define and handle:

      * `AIServiceError` (Gemini failures).
      * `PlanValidationError`.
      * User input validation errors.

20. **Logging and observability**

    * Log LLM calls (prompt + truncated response where safe).
    * Log validation failures and unexpected states.

21. **Refinement and tuning**

    * Adjust prompts in `GeminiClient` based on observed behaviour.
    * Tighten validation rules if needed.

---

## 7. Future Steps (Optional)

22. Support variable durations (e.g. 10 or 15 minutes).

23. Enrich `GoalProfile` (equipment, experience level, schedule).

24. Add analytics endpoints or internal logging for user completion rates.

This sequence keeps risk low: start from stable foundations (core, exercises, domain), then build agents, then API, with tests at each layer.
