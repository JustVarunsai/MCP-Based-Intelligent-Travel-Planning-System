"""
Saved trips CRUD + agent reasoning audit trail.
"""
import logging

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.config import config

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api/trips", tags=["trips"])


class TripSummary(BaseModel):
    id: str
    destination: str
    duration_days: int
    budget_usd: int
    status: str
    created_at: str | None


def _get_crud_or_404():
    if not config.database_url:
        raise HTTPException(status_code=503, detail="database not configured")
    from backend.database.crud import UserCRUD, TripCRUD, AgentLogCRUD
    return UserCRUD(), TripCRUD(), AgentLogCRUD()


def _serialise_trip(trip: dict) -> dict:
    """Make a trip row JSON-safe."""
    out = dict(trip)
    for k, v in list(out.items()):
        if hasattr(v, "isoformat"):
            out[k] = v.isoformat()
    return out


@router.get("")
async def list_trips(user_email: str = Query("default@travel.app")):
    """List all saved trips for the user."""
    user_crud, trip_crud, _ = _get_crud_or_404()
    user = user_crud.get_or_create(user_email)
    trips = trip_crud.get_user_trips(user["id"])
    return {"count": len(trips), "trips": [_serialise_trip(t) for t in trips]}


@router.get("/{trip_id}")
async def get_trip(trip_id: str):
    """Return one saved trip including its full markdown itinerary."""
    _, trip_crud, _ = _get_crud_or_404()
    trip = trip_crud.get_trip(trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="trip not found")
    return _serialise_trip(trip)


@router.delete("/{trip_id}")
async def delete_trip(trip_id: str):
    """Delete a saved trip."""
    _, trip_crud, _ = _get_crud_or_404()
    trip_crud.delete_trip(trip_id)
    return {"ok": True, "deleted": trip_id}


@router.get("/{trip_id}/logs")
async def trip_logs(trip_id: str):
    """Agent reasoning audit trail for a specific trip."""
    _, _, log_crud = _get_crud_or_404()
    logs = log_crud.get_trip_logs(trip_id)
    return {"trip_id": trip_id, "count": len(logs), "logs": [_serialise_trip(l) for l in logs]}
