"""
Database CRUD smoke tests. Skipped unless SUPABASE_DATABASE_URL is set.
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.mark.skipif(
    not os.getenv("SUPABASE_DATABASE_URL"),
    reason="Supabase not configured — set SUPABASE_DATABASE_URL to run",
)
def test_user_crud_roundtrip():
    from backend.database.crud import UserCRUD

    crud = UserCRUD()
    user = crud.get_or_create("pytest@example.com", "Pytest User")
    assert user["email"] == "pytest@example.com"

    same = crud.get_or_create("pytest@example.com")
    assert same["id"] == user["id"]


@pytest.mark.skipif(
    not os.getenv("SUPABASE_DATABASE_URL"),
    reason="Supabase not configured",
)
def test_trip_crud_roundtrip():
    from backend.database.crud import UserCRUD, TripCRUD

    user = UserCRUD().get_or_create("pytest@example.com")
    trip_crud = TripCRUD()

    trip = trip_crud.save_trip(
        user_id=user["id"],
        destination="Test City",
        duration_days=3,
        budget_usd=1000,
        preferences="testing",
    )
    assert trip["destination"] == "Test City"

    trips = trip_crud.get_user_trips(user["id"])
    assert any(str(t["id"]) == str(trip["id"]) for t in trips)

    trip_crud.delete_trip(trip["id"])
