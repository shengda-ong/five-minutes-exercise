# Architecture Plan for The 5 Minutes Exercise Backend

This document captures the **rationale**, **trade-offs**, and **decision history** behind the proposed backend structure. It acts as a living architectural record that can be iterated on as the project evolves.

---

## 1. Project Context

**The 5 Minutes Exercise** is a mobile-first application that generates short, personalised workout plans. The backend must:

* Store a curated database of exercises
* Interpret user goals via Gemini (AI-assisted reasoning)
* Filter exercises based on constraints (injuries, equipment limits, intensity)
* Produce a 5-minute plan *using only known exercises*
* Return predictable, stable exercise IDs for the mobile UI

Given this scope, the backend needs to feel professional but remain small and approachable for a portfolio project.

---

## 2. Design Goals

### 2.1 Clarity and Maintainability

The structure must be easy for reviewers to read and understand quickly. Separation of concerns is essential, but we avoid enterprise-level overengineering.

### 2.2 Extensibility

The app should support future additions, such as:

* User profiles
* Additional injury types
* More exercise attributes
* Extended workout durations
* Alternative fitness goals (strength, mobility)

### 2.3 Testability

The architecture encourages:

* Clear boundaries for mocking Gemini
* Testing business logic without touching Django ORM
* End-to-end API testing using small fixture datasets

### 2.4 Realistically Scalable (but still small)

The project mirrors the patterns of mature systems but keeps the implementation minimal and modular.

---

## 3. High-Level Architecture Overview

The backend is organized into **three main functional layers** plus infrastructure:

1. **API Layer** – DRF views/serializers defining the external interface.
2. **Application/Service Layer** – Orchestrates workflows (e.g., plan generation).
3. **Domain Layer** – Pure Python classes modeling the business logic.
4. **Infrastructure Layer** – Integrations (Django models, Gemini client).

This separation enables modularity without complicating the codebase.

---

## 4. Modular Components (Apps)

### 4.1 `core/`

**Purpose:** Cross-cutting infrastructure shared across apps.

Contains:

* `GeminiClient` (wrapper around Google API)
* Shared exceptions
* Future cross-cutting utilities

**Rationale:** AI integration is isolated so it can be easily mocked or replaced.

---

### 4.2 `exercises/`

**Purpose:** Houses the exercise catalogue and database interactions.

Contains:

* Django models: `Exercise`, `MuscleGroup`, `Tag`, `Contraindication`
* `ExerciseRepository` for filtering and fetching exercises
* Serializers and admin bindings

**Rationale:** Exercise data is the backbone of the app; placing it in a dedicated module keeps it organized and makes testing easier.

---

### 4.3 `plans/`

**Purpose:** Holds the domain logic and recommendation flow.

Contains:

* Domain models (`GoalProfile`, `WorkoutPlan`, `PlanExercise`)
* `RecommendationService` orchestrating AI + repository
* Validation logic
* API endpoints for plan generation

**Rationale:** Keeps workout logic separate from data storage, making it a clean, testable module.

---

### 4.4 `users/` (Optional for later)

**Purpose:** Store long-term preferences and history.

**Rationale:** Modular, optional, and easy to add when needed.

---

## 5. Rationale Behind Key Architectural Decisions

### 5.1 Why Multiple Django Apps?

* Encourages separation of concerns
* Matches Django best practices
* Helps with test organization
* Keeps the codebase readable for reviewers

### 5.2 Why OOP, Not Functional?

* The system manages entities (exercises, plans, goal profiles)
* OOP models domain concepts naturally
* Service classes provide clean dependency injection for testing
* Minimal latency difference given network-bound workloads

### 5.3 Why Use a Domain Layer?

* Keeps business logic independent of frameworks
* Easier to unit-test
* Aligns with real-world backend architecture patterns

### 5.4 Why Wrap Gemini in `GeminiClient`?

* AI responses must follow strict rules (no invented exercises)
* Wrapping provides:

  * prompt templates
  * response schema validation
  * mockable interface for tests

### 5.5 Why a Repository Pattern for Exercises?

* Avoids scattering ORM queries
* Enables swapping database logic
* Makes filtering rules testable independently

---

## 6. Proposed File Structure

```text
backend/
├─ core/
│  ├─ gemini_client.py
│  ├─ exceptions.py
│  └─ tests/
│
├─ exercises/
│  ├─ models.py
│  ├─ services.py
│  ├─ serializers.py
│  ├─ admin.py
│  ├─ urls.py
│  └─ tests/
│
├─ plans/
│  ├─ domain.py
│  ├─ services.py
│  ├─ serializers.py
│  ├─ views.py
│  ├─ urls.py
│  └─ tests/
│
└─ users/ (future)
```

---

## 7. Testing Approach

### 7.1 Unit Tests

* `GoalProfile` parsing
* Exercise filtering logic
* Plan validation rules
* Recommendation service using **mocked Gemini** and fake repositories

### 7.2 Integration Tests

* End-to-end plan generation with a small fixture DB
* Mocked Gemini to produce deterministic output

### 7.3 API Tests

* `/api/v1/plans/` happy path + constraint handling
* `/api/v1/exercises/`

**Rationale:** This layered testing approach gives strong coverage with minimal complexity.

---

## 8. Future Extensibility

The design can scale naturally to include:

* User accounts & saved plans
* AI-powered plan evaluation
* More sophisticated injury modeling
* Multi-day training programs
* Genre-specific plans (e.g., stretching-only, chair-only)

The current architecture is small but ready for growth.

---

## 9. Open Questions (for future decisions)

* Should plan generation allow non-5-minute durations?
* Should exercises support equipment lists (e.g., dumbbells)?
* Should injuries be a separate table or represented as tags?
* Should Gemini ranking logic be moved into a strategy pattern?

These can be revisited once MVP is complete.

---

## 10. Agentic Architecture (High-Level)

To keep the system easy to understand and avoid any single "superman" component, the backend is designed in an **agentic** way.

Here, an *agent* is simply a focused service class with one clear job. These agents work together like a small team:

* **GoalUnderstandingAgent** (in `plans/` or `core/`)

  * Talks to Gemini to turn the user's free-text goal into a structured `GoalProfile`.
  * Example: from *"I want to burn calories but I have knee pain"* to a profile that says:

    * primary_goal: calorie_burn
    * duration: 300 seconds
    * constraints: knee-friendly, low impact, no jumping

* **ExerciseFilteringAgent / ExerciseRepository** (in `exercises/`)

  * Reads the exercise database and filters it based on the `GoalProfile`.
  * Removes exercises that are not knee-friendly, too high impact, or require unavailable equipment.
  * Returns a clean list of candidate exercises.

* **PlanGenerationAgent** (in `plans/`)

  * Uses Gemini to choose a sequence of exercises only from the candidate list.
  * Ensures the plan tries to match the target duration (5 minutes) and the goal.
  * Produces a raw plan structure (exercise IDs with durations).

* **PlanValidationAgent** (in `plans/`)

  * Checks that the plan is safe and valid:

    * No unknown exercise IDs
    * Total time is in an acceptable range around 5 minutes
    * All constraints (e.g. knee-friendly) are respected

* **RecommendationService** (in `plans/`)

  * This is the orchestrator that coordinates all agents:

    1. Ask `GoalUnderstandingAgent` to parse the user goal.
    2. Ask `ExerciseFilteringAgent` / `ExerciseRepository` for allowed exercises.
    3. Ask `PlanGenerationAgent` to assemble a plan using those exercises.
    4. Ask `PlanValidationAgent` to double-check the plan.
    5. Return a final `WorkoutPlan` to the API layer.

This design keeps each piece small and understandable, while still looking like a serious, real-world backend architecture.

---

## 11. How to Mentally Model the System (Beginner-Friendly)

You can think of the backend as a conversation between parts:

1. **Mobile app → API**: "Here is the user's goal text and profile. Please give me a 5-minute workout."
2. **API → RecommendationService**: "Create a workout plan for this input."
3. **RecommendationService → Agents**:

   * "GoalUnderstandingAgent, what does this user really want?"
   * "ExerciseFilteringAgent, which exercises are safe and relevant?"
   * "PlanGenerationAgent, build a sequence only from these exercises."
   * "PlanValidationAgent, is this plan valid?"
4. **RecommendationService → API**: "Here is a safe, valid plan."
5. **API → Mobile app**: returns JSON containing the structured workout.

At no point does Gemini invent new exercises, because:

* It only sees the list of allowed exercises from the database.
* The plan is validated on the server before sending it back.

This mental model should help you explain the system during interviews or when you revisit the project later.

---

## 12. Project Packaging & Repository Hygiene (for Future Reference)

To ensure the backend behaves correctly during testing and development, and to keep the repository clean, these rules apply:

### 12.1 Python Package Structure Rules

* The **project root** for the backend is the `backend/` folder.
* The `backend/` folder should **NOT** contain an `__init__.py` file.
  This ensures `backend/` behaves as a project root and avoids module import conflicts during testing.
* Each Django app folder (e.g., `core/`, `exercises/`, `plans/`) **must** contain an `__init__.py` file so Python recognizes them as importable modules.
* When running tests from inside `backend/`, imports like:

  ```python
  from core.gemini_client import GeminiClient
  ```

  work reliably.

### 12.2 .gitignore Practices

The repository should ignore:

* `__pycache__/` folders
* Python bytecode (`*.pyc`)
* Virtual environments (`.venv/`, `env/`)
* Test caches (`.pytest_cache/`)
* Environment variable files (`.env`, `backend/config/.env`)
* IDE settings (`.vscode/`, `.idea/`)
* Build artifacts (`dist/`, `build/`)
* Coverage reports (`htmlcov/`, `.coverage`)

A clean `.gitignore` keeps your commits focused and avoids accidentally exposing secrets or clutter.

### 12.3 Test Execution Rules

* Use `pytest` from inside the `backend/` folder:

  ```bash
  cd backend
  pytest
  ```
* This ensures the correct module resolution path and avoids import errors.
* Tests should import modules using absolute imports relative to `backend/`, e.g.:

  ```python
  from core.gemini_client import GeminiClient
  ```

### 12.4 Why These Rules Matter

These packaging and hygiene rules:

* Prevent confusing import errors
* Ensure deterministic test behavior
* Keep the repository clean and professional
* Make it easy for others (and future you) to understand the structure
* Follow standard Python and Django project conventions

---

## 13. Conclusion

This architecture balances:

* **Clarity** – each module and agent has a clear role.
* **Modularity** – Django apps and service classes keep concerns separated.
* **Agentic design** – several focused agents collaborate instead of one giant object.
* **Testability** – each agent and service can be tested in isolation.
* **Realism** – the structure mirrors patterns used in real production backends, while staying small enough for a portfolio project.

This document should be updated as you refine the design or learn more. Treat it as the living memory of why the backend looks the way it does.
