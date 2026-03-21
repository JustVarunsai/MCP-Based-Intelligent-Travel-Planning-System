"""
Placeholder tests for database CRUD operations.
These need a running Supabase instance with the schema set up.
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.mark.skipif(
    not os.getenv("SUPABASE_URL"),
    reason="Supabase not configured — set SUPABASE_URL and SUPABASE_KEY to run"
)
def test_user_crud():
    from database.crud import UserCRUD
    crud = UserCRUD()
    user = crud.get_or_create("test@example.com", "Test User")
    assert user["email"] == "test@example.com"

    # calling again should return the same user
    same = crud.get_or_create("test@example.com")
    assert same["id"] == user["id"]


@pytest.mark.skipif(
    not os.getenv("SUPABASE_URL"),
    reason="Supabase not configured"
)
def test_trip_crud():
    from database.crud import UserCRUD, TripCRUD
    user = UserCRUD().get_or_create("test@example.com")
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
    assert any(t["id"] == trip["id"] for t in trips)

    # cleanup
    trip_crud.delete_trip(trip["id"])
