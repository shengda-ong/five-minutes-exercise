# The 5 Minutes Exercise – Backend

Backend for **The 5 Minutes Exercise**, a mobile-focused app that delivers
personalised 5-minute workout plans.

Users describe their goal in natural language (e.g.  
> “My goal is to lose calories, but I have knee injuries.”)  

The backend then:

1. Uses **Gemini** to interpret the goal and constraints
2. Filters a curated exercise database (no invented exercises)
3. Assembles a 5-minute set of knee-friendly, low-impact exercises
4. Returns a structured plan for the mobile app to render

The AI is *constrained*: it can only select from stored exercises, never
create new ones. This allows the frontend to rely on stable exercise IDs and
assets (animations, icons, etc).

---

## ✨ Features (MVP)

- Django backend (Python 3.13)
- Modular architecture with clear separation of concerns
- Exercise database:
  - name, description
  - default duration
  - calories estimate
  - muscle groups
  - tags (impact level, equipment, injury constraints)
- Gemini-powered recommendation engine:
  - parses natural language goals into structured `GoalProfile`s
  - filters exercises based on constraints (e.g. “knee injury”, “low impact”)
  - builds a 5-minute plan using **only known exercises**
- REST API for mobile clients (Django REST Framework)
- Testable design:
  - services with clear interfaces
  - Gemini integration mockable in tests

---

## 🔧 Tech Stack

- **Language:** Python 3.13
- **Framework:** Django (with Django REST Framework)
- **Database:** PostgreSQL (SQLite OK for local dev)
- **AI:** Google Gemini (`google-genai`)
- **Config:** `python-dotenv` for local `.env` files
- **Testing:** `pytest` (or Django’s test runner) + requests client

---

## 🏗️ Architecture Overview

The backend is intentionally small but structured like a real service.

### High-level layers

- **API layer**  
  Django REST Framework views / viewsets and serializers.

- **Application / Service layer**  
  Orchestrates workflows:
  - `RecommendationService`
  - `ExerciseRepository`

- **Domain layer**  
  Plain Python classes representing:
  - `GoalProfile`
  - `Plan` / `PlanExercise`
  - Domain validation & business rules.

- **Infrastructure layer**  
  Concrete integrations:
  - Django ORM models (`Exercise`, `MuscleGroup`, etc.)
  - `GeminiClient` wrapper around the Google API.

### Django apps

- `core/`  
  Shared infrastructure:
  - `GeminiClient`
  - base exceptions, utilities

- `exercises/`  
  Exercise data and access:
  - Models: `Exercise`, `MuscleGroup`, `Tag`, `Contraindication`
  - Service: `ExerciseRepository`
  - Serializers for API exposure

- `plans/`  
  Recommendation logic:
  - Domain models: `GoalProfile`, `WorkoutPlan`, `PlanExercise`
  - Service: `RecommendationService`
  - API views/serializers for the `/api/v1/plans/` endpoint

- `users/` (optional / later)  
  User profiles, stored constraints, history.

This structure keeps the project small but clearly modular.

---

## 📁 Project Structure

Planned layout (simplified):

```text
backend/
├─ manage.py
├─ pyproject.toml / requirements.txt
├─ config/
│  └─ .env                 # local settings (not committed)
├─ five_minutes_exercise/   # Django project settings
│  ├─ __init__.py
│  ├─ settings.py
│  ├─ urls.py
│  └─ asgi.py
│
├─ core/
│  ├─ __init__.py
│  ├─ gemini_client.py
│  ├─ exceptions.py
│  └─ tests/
│
├─ exercises/
│  ├─ __init__.py
│  ├─ models.py
│  ├─ services.py          # ExerciseRepository
│  ├─ serializers.py
│  ├─ admin.py
│  ├─ urls.py
│  └─ tests/
│
├─ plans/
│  ├─ __init__.py
│  ├─ domain.py            # GoalProfile, WorkoutPlan, PlanExercise
│  ├─ services.py          # RecommendationService
│  ├─ serializers.py
│  ├─ views.py             # /api/v1/plans/
│  ├─ urls.py
│  └─ tests/
│
└─ users/                  # (optional)
   ├─ __init__.py
   ├─ models.py
   ├─ serializers.py
   ├─ views.py
   ├─ urls.py
   └─ tests/
