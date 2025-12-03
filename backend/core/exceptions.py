class AIServiceError(Exception):
    """
    Raised when:
    - Gemini returns invalid JSON
    - Gemini refuses instructions
    - The JSON schema is missing required keys
    - The model call fails (network error, API issue)
    """
    pass


class ValidationError(Exception):
    """
    Raised when a plan or goal profile fails validation
    (e.g., exercise IDs don't match database entries,
    duration is out of bounds, constraints violated).
    """
    pass


class RepositoryError(Exception):
    """
    Raised when something goes wrong inside the ExerciseRepository
    (e.g., invalid filters, missing data, DB issues).
    """
    pass
