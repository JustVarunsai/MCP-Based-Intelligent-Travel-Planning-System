"""
CRUD operations using SQLAlchemy directly against the Supabase Postgres db.
"""
from typing import List, Optional
from sqlalchemy import text
from database.supabase_client import get_engine, ensure_tables


class UserCRUD:
    def __init__(self):
        ensure_tables()
        self.engine = get_engine()

    def get_or_create(self, email: str, display_name: str = "") -> dict:
        with self.engine.begin() as conn:
            row = conn.execute(
                text("SELECT * FROM users WHERE email = :e"), {"e": email}
            ).mappings().first()
            if row:
                return dict(row)
            name = display_name or email.split("@")[0]
            new = conn.execute(
                text("""
                    INSERT INTO users (email, display_name)
                    VALUES (:e, :n)
                    RETURNING *
                """),
                {"e": email, "n": name},
            ).mappings().first()
            return dict(new)


class TripCRUD:
    def __init__(self):
        ensure_tables()
        self.engine = get_engine()

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
        import json as _json
        with self.engine.begin() as conn:
            row = conn.execute(
                text("""
                    INSERT INTO trips (
                        user_id, destination, duration_days, budget_usd,
                        preferences, itinerary_json, itinerary_markdown,
                        total_estimated_cost, status
                    )
                    VALUES (
                        :uid, :dest, :days, :bgt,
                        :prefs, :ij, :im,
                        :cost, 'completed'
                    )
                    RETURNING *
                """),
                {
                    "uid": user_id,
                    "dest": destination,
                    "days": duration_days,
                    "bgt": budget_usd,
                    "prefs": preferences,
                    "ij": _json.dumps(itinerary_json) if itinerary_json else None,
                    "im": itinerary_markdown,
                    "cost": total_estimated_cost,
                },
            ).mappings().first()
            return dict(row)

    def get_user_trips(self, user_id: str) -> List[dict]:
        with self.engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT * FROM trips
                    WHERE user_id = :uid
                    ORDER BY created_at DESC
                """),
                {"uid": user_id},
            ).mappings().all()
            return [dict(r) for r in rows]

    def get_trip(self, trip_id: str) -> Optional[dict]:
        with self.engine.connect() as conn:
            row = conn.execute(
                text("SELECT * FROM trips WHERE id = :id"),
                {"id": trip_id},
            ).mappings().first()
            return dict(row) if row else None

    def delete_trip(self, trip_id: str):
        with self.engine.begin() as conn:
            conn.execute(text("DELETE FROM trips WHERE id = :id"), {"id": trip_id})


class AgentLogCRUD:
    def __init__(self):
        ensure_tables()
        self.engine = get_engine()

    def log_event(
        self,
        trip_id: str,
        agent_name: str,
        event_type: str,
        tool_name: str = None,
        content: str = None,
        duration_ms: int = None,
    ) -> dict:
        with self.engine.begin() as conn:
            row = conn.execute(
                text("""
                    INSERT INTO agent_logs (
                        trip_id, agent_name, event_type, tool_name, content, duration_ms
                    )
                    VALUES (:tid, :an, :et, :tn, :c, :d)
                    RETURNING *
                """),
                {
                    "tid": trip_id,
                    "an": agent_name,
                    "et": event_type,
                    "tn": tool_name,
                    "c": content,
                    "d": duration_ms,
                },
            ).mappings().first()
            return dict(row)

    def get_trip_logs(self, trip_id: str) -> List[dict]:
        with self.engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT * FROM agent_logs
                    WHERE trip_id = :tid
                    ORDER BY created_at
                """),
                {"tid": trip_id},
            ).mappings().all()
            return [dict(r) for r in rows]
