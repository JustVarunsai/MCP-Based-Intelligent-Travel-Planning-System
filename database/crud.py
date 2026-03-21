from typing import List, Optional
from database.supabase_client import get_supabase


class UserCRUD:
    """Handles user profile operations in Supabase."""

    def __init__(self):
        self.client = get_supabase()

    def get_or_create(self, email: str, display_name: str = "") -> dict:
        result = (
            self.client.table("users")
            .select("*")
            .eq("email", email)
            .execute()
        )
        if result.data:
            return result.data[0]
        # create a new user
        data = {"email": email, "display_name": display_name or email.split("@")[0]}
        return self.client.table("users").insert(data).execute().data[0]

    def update_preferences(self, user_id: str, preferences: list) -> dict:
        return (
            self.client.table("users")
            .update({"travel_preferences": preferences})
            .eq("id", user_id)
            .execute()
            .data[0]
        )


class TripCRUD:
    """Handles saved trip operations in Supabase."""

    def __init__(self):
        self.client = get_supabase()

    def save_trip(
        self,
        user_id: str,
        destination: str,
        duration_days: int,
        budget_usd: int,
        preferences: str,
        itinerary_json: dict = None,
        itinerary_markdown: str = "",
        total_estimated_cost: float = 0,
    ) -> dict:
        data = {
            "user_id": user_id,
            "destination": destination,
            "duration_days": duration_days,
            "budget_usd": budget_usd,
            "preferences": preferences,
            "itinerary_json": itinerary_json,
            "itinerary_markdown": itinerary_markdown,
            "total_estimated_cost": total_estimated_cost,
            "status": "completed",
        }
        return self.client.table("trips").insert(data).execute().data[0]

    def get_user_trips(self, user_id: str) -> List[dict]:
        return (
            self.client.table("trips")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
            .data
        )

    def get_trip(self, trip_id: str) -> Optional[dict]:
        result = (
            self.client.table("trips")
            .select("*")
            .eq("id", trip_id)
            .single()
            .execute()
        )
        return result.data

    def delete_trip(self, trip_id: str):
        self.client.table("trips").delete().eq("id", trip_id).execute()


class AgentLogCRUD:
    """Stores per-trip agent activity logs."""

    def __init__(self):
        self.client = get_supabase()

    def log_event(
        self,
        trip_id: str,
        agent_name: str,
        event_type: str,
        tool_name: str = None,
        content: str = None,
        duration_ms: int = None,
    ) -> dict:
        data = {
            "trip_id": trip_id,
            "agent_name": agent_name,
            "event_type": event_type,
            "tool_name": tool_name,
            "content": content,
            "duration_ms": duration_ms,
        }
        return self.client.table("agent_logs").insert(data).execute().data[0]

    def get_trip_logs(self, trip_id: str) -> List[dict]:
        return (
            self.client.table("agent_logs")
            .select("*")
            .eq("trip_id", trip_id)
            .order("created_at")
            .execute()
            .data
        )
