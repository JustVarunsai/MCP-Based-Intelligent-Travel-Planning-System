"""
Input validation helpers for trip parameters.
"""


def validate_trip_input(destination: str, num_days: int, budget: int) -> list:
    """
    Returns a list of error messages. Empty list means all good.
    """
    errors = []
    if not destination or not destination.strip():
        errors.append("Destination is required.")
    if num_days < 1 or num_days > 30:
        errors.append("Trip duration must be between 1 and 30 days.")
    if budget < 100:
        errors.append("Budget must be at least $100.")
    return errors
